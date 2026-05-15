from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db.models import Sum
from datetime import date as date_type, datetime  # Renommer pour éviter le conflit
from decimal import Decimal
import json

# Import des modèles
from .models import (
    AccessCode, Ingredient, RecetteGateau, 
    RecetteIngredient, Employe, DetailJournee, Vente
)

# Import des formulaires
from .forms import AccessCodeForm, DetailJourneeForm, EmployeForm

# Import des utilitaires
from .utils import generate_pdf_report

# ==================== AUTHENTIFICATION ====================

def access_code_view(request):
    """Vue pour le code d'accès"""
    if request.session.get('access_granted'):
        return redirect('home')
    
    if request.method == 'POST':
        code = request.POST.get('access_code', '').strip()
        
        # Vérifier le nombre de tentatives (rate limiting)
        attempts = request.session.get('access_attempts', 0)
        if attempts >= 5:
            last_attempt = request.session.get('last_attempt_time')
            if last_attempt:
                last_time = datetime.fromisoformat(last_attempt)
                if (datetime.now() - last_time).seconds < 300:
                    return render(request, 'calculator/access_code.html', {
                        'locked': True,
                        'message': 'Trop de tentatives. Réessayez dans 5 minutes.'
                    })
                else:
                    request.session['access_attempts'] = 0
        
        access = AccessCode.get_current_code()
        
        if access and access.check_code(code):
            request.session['access_granted'] = True
            request.session['access_attempts'] = 0
            request.session['access_time'] = timezone.now().isoformat()
            messages.success(request, '✅ Accès autorisé !')
            return redirect('home')
        else:
            request.session['access_attempts'] = attempts + 1
            request.session['last_attempt_time'] = datetime.now().isoformat()
            messages.error(request, f'❌ Code incorrect. Tentative {attempts + 1}/5')
    
    return render(request, 'calculator/access_code.html')

def logout_view(request):
    """Déconnexion"""
    request.session.flush()
    messages.info(request, 'Vous êtes déconnecté')
    return redirect('access_code')

# ==================== PAGE D'ACCUEIL ====================

def home(request):
    """Page d'accueil avec les recettes"""
    if not request.session.get('access_granted'):
        return redirect('access_code')
    
    recettes = RecetteGateau.objects.all().prefetch_related('recetteingredient_set__ingredient')
    today = date_type.today()  # Utiliser date_type.today()
    journee_today = DetailJournee.objects.filter(date=today).first()
    
    context = {
        'recettes': recettes,
        'journee_today': journee_today,
    }
    return render(request, 'calculator/home.html', context)

# ==================== GESTION DES JOURNÉES ====================

@csrf_protect
def nouvelle_journee(request):
    """Créer une nouvelle journée"""
    if not request.session.get('access_granted'):
        return redirect('access_code')
    
    today = date_type.today()  # Utiliser date_type.today()
    
    # Vérifier si une journée existe déjà pour aujourd'hui
    if DetailJournee.objects.filter(date=today).exists():
        messages.warning(request, '⚠️ Une journée existe déjà pour aujourd\'hui')
        return redirect('journee_detail', date_str=today.isoformat())
    
    if request.method == 'POST':
        form = DetailJourneeForm(request.POST)
        if form.is_valid():
            try:
                # Créer la journée
                journee = form.save(commit=False)
                journee.date = today
                journee.save()
                
                # Sauvegarder les employés
                employe_noms = request.POST.getlist('employe_nom[]')
                employe_salaires = request.POST.getlist('employe_salaire[]')
                
                for nom, salaire in zip(employe_noms, employe_salaires):
                    if nom.strip() and salaire:
                        employe = Employe.objects.create(
                            nom=nom.strip(),
                            salaire_journalier=Decimal(salaire)
                        )
                        journee.employes.add(employe)
                
                # Sauvegarder les ventes
                recettes = RecetteGateau.objects.all()
                for recette in recettes:
                    quantite_key = f'vente_{recette.id}'
                    quantite = request.POST.get(quantite_key, '0')
                    try:
                        quantite = int(quantite)
                    except (ValueError, TypeError):
                        quantite = 0
                        
                    if quantite > 0:
                        Vente.objects.create(
                            detail_journee=journee,
                            recette_gateau=recette,
                            quantite_vendue=quantite
                        )
                
                messages.success(request, '✅ Journée créée avec succès !')
                return redirect('journee_detail', date=today.isoformat())
                
            except Exception as e:
                messages.error(request, f'❌ Erreur lors de la création : {str(e)}')
    else:
        form = DetailJourneeForm()
    
    recettes = RecetteGateau.objects.all()
    context = {
        'form': form,
        'recettes': recettes,
        'today': today,
    }
    return render(request, 'calculator/nouvelle_journee.html', context)

def journee_detail(request, date_str):  
    """Afficher le détail d'une journée"""
    if not request.session.get('access_granted'):
        return redirect('access_code')
    
    try:
        journee_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, '❌ Format de date invalide')
        return redirect('home')
    
    journee = get_object_or_404(DetailJournee, date=journee_date)
    from datetime import date as date_type  # Import local
    today = date_type.today()
    is_today = (journee.date == today)

    if journee.chiffre_affaire > 0:
        marge = (journee.benefice / journee.chiffre_affaire * 100)
    else:
        marge = 0
    
    context = {
        'journee': journee,
        'is_today': is_today,
        'marge': marge,
    }
    return render(request, 'calculator/journee_detail.html', context)

@csrf_protect
def modifier_journee(request, date_str):  
    """Modifier une journée"""
    if not request.session.get('access_granted'):
        return redirect('access_code')
    
    try:
        journee_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, '❌ Format de date invalide')
        return redirect('home')
    
    journee = get_object_or_404(DetailJournee, date=journee_date)
    
    if request.method == 'POST':
        # Mettre à jour les frais fixes
        journee.frais_local = Decimal(request.POST.get('frais_local', 350))
        journee.frais_electricite_impots = Decimal(request.POST.get('frais_electricite_impots', 150))
        journee.save()
        
        # Mettre à jour les ventes
        recettes = RecetteGateau.objects.all()
        for recette in recettes:
            quantite_key = f'vente_{recette.id}'
            quantite = request.POST.get(quantite_key, '0')
            try:
                quantite = int(quantite)
            except (ValueError, TypeError):
                quantite = 0
            
            vente, created = Vente.objects.get_or_create(
                detail_journee=journee,
                recette_gateau=recette,
                defaults={'quantite_vendue': quantite}
            )
            
            if not created:
                if quantite > 0:
                    vente.quantite_vendue = quantite
                    vente.save()
                else:
                    vente.delete()
        
        messages.success(request, '✅ Journée mise à jour avec succès !')
        return redirect('journee_detail', date_str=journee_date.isoformat())
    
    recettes = RecetteGateau.objects.all()
    context = {
        'journee': journee,
        'recettes': recettes,
    }
    return render(request, 'calculator/modifier_journee.html', context)

@require_POST
def supprimer_journee(request, date_str):  # Changer 'date' en 'date_str'
    """Supprimer une journée"""
    if not request.session.get('access_granted'):
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    try:
        journee_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Format de date invalide'}, status=400)
    
    journee = get_object_or_404(DetailJournee, date=journee_date)
    journee.delete()
    messages.success(request, '🗑️ Journée supprimée avec succès !')
    return JsonResponse({'success': True})

# ==================== HISTORIQUE ====================

def historique_journees(request):
    """Afficher l'historique des journées"""
    if not request.session.get('access_granted'):
        return redirect('access_code')
    
    journees = DetailJournee.objects.all().order_by('-date')
    
    context = {
        'journees': journees,
    }
    return render(request, 'calculator/historique.html', context)

# ==================== EXPORT PDF ====================

def export_pdf(request, date_str):  # Changer 'date' en 'date_str'
    """Exporter le rapport en PDF"""
    if not request.session.get('access_granted'):
        return redirect('access_code')
    
    try:
        journee_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, '❌ Format de date invalide')
        return redirect('home')
    
    journee = get_object_or_404(DetailJournee, date=journee_date)
    return generate_pdf_report(journee)

# ==================== API (optionnel) ====================

def api_journees_list(request):
    """API pour la liste des journées"""
    if not request.session.get('access_granted'):
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    journees = DetailJournee.objects.all().values('date', 'benefice').order_by('-date')
    return JsonResponse(list(journees), safe=False)

def api_ventes(request):
    """API pour les ventes du jour"""
    if not request.session.get('access_granted'):
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    
    today = date_type.today()  # Utiliser date_type.today()
    journee = DetailJournee.objects.filter(date=today).first()
    
    if not journee:
        return JsonResponse({'error': 'Pas de journée aujourd\'hui'}, status=404)
    
    ventes = []
    for vente in journee.vente_set.all():
        ventes.append({
            'recette': vente.recette_gateau.nom,
            'quantite': vente.quantite_vendue,
            'total': float(vente.total_vente())
        })
    
    return JsonResponse(ventes, safe=False)