from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import (
    AccessCode, Ingredient, RecetteGateau, 
    RecetteIngredient, Employe, DetailJournee, Vente
)

# ==================== ACCESS CODE ====================

@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'code_preview']
    readonly_fields = ['code_hash', 'created_at']
    
    def code_preview(self, obj):
        return "••••••••"  # Ne jamais afficher le code en clair
    code_preview.short_description = "Code"
    
    def has_add_permission(self, request):
        # Empêcher la création si un code existe déjà
        if AccessCode.objects.exists():
            return False
        return True

# ==================== INGRÉDIENTS ====================

class RecetteIngredientInline(admin.TabularInline):
    model = RecetteIngredient
    extra = 1
    fields = ['ingredient', 'quantite_gramme']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'poids_gramme', 'prix_kg', 'prix_gramme_display']
    list_filter = ['nom']
    search_fields = ['nom']
    ordering = ['nom']
    
    def prix_gramme_display(self, obj):
        return f"{obj.prix_par_gramme():.3f} DA/g"
    prix_gramme_display.short_description = "Prix au gramme"

# ==================== RECETTES ====================

@admin.register(RecetteGateau)
class RecetteGateauAdmin(admin.ModelAdmin):
    list_display = ['nom', 'image_preview', 'prix_vente_display', 
                   'nombre_unites', 'nombre_ingredients']
    list_filter = ['nom']
    search_fields = ['nom']
    inlines = [RecetteIngredientInline]
    readonly_fields = ['prix_revient_calculated']
    
    fieldsets = (
        ('Informations Générales', {
            'fields': ('nom', 'image')
        }),
        ('Détails de Production', {
            'fields': ('nombre_unites_resultantes',)
        }),
        ('Prix et Frais', {
            'fields': ('prix_vente_unitaire', 'frais_emballage_unitaire', 'prix_revient_calculated'),
            'description': 'Le prix de revient est calculé automatiquement'
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "Pas d'image"
    image_preview.short_description = "Image"
    
    def prix_vente_display(self, obj):
        # CORRECTION : Ne pas utiliser format_html avec {:f} sur un objet déjà formaté
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{} DA</span>',
            round(obj.prix_vente_unitaire, 2)
        )
    prix_vente_display.short_description = "Prix de vente"
    prix_vente_display.admin_order_field = 'prix_vente_unitaire'
    
    def nombre_unites(self, obj):
        return f"{obj.nombre_unites_resultantes} unités"
    nombre_unites.short_description = "Unités"
    
    def nombre_ingredients(self, obj):
        count = obj.ingredients.count()
        return f"{count} ingrédient(s)"
    nombre_ingredients.short_description = "Ingrédients"
    
    def prix_revient_calculated(self, obj):
        if obj.pk:
            prix = obj.calculer_prix_revient_unitaire()
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
                '<strong>Prix de revient unitaire :</strong> '
                '<span style="color: #dc3545; font-size: 1.2em;">{} DA</span><br>'
                '<small class="text-muted">(Incluant les ingrédients et l\'emballage)</small>'
                '</div>',
                round(prix, 2)
            )
        return "Enregistrez d'abord la recette pour voir le prix de revient"
    prix_revient_calculated.short_description = "Prix de revient calculé"

# ==================== EMPLOYÉS ====================

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'salaire_display']
    search_fields = ['nom']
    
    def salaire_display(self, obj):
        return format_html(
            '<span style="color: #007bff; font-weight: bold;">{} DA</span>',
            round(obj.salaire_journalier, 2)
        )
    salaire_display.short_description = "Salaire journalier"

# ==================== VENTES (Inline) ====================

class VenteInline(admin.TabularInline):
    model = Vente
    extra = 1
    fields = ['recette_gateau', 'quantite_vendue', 'total_vente_calculated']
    readonly_fields = ['total_vente_calculated']
    
    def total_vente_calculated(self, obj):
        if obj.pk:
            total = obj.total_vente()
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{} DA</span>',
                round(total, 2)
            )
        return "-"
    total_vente_calculated.short_description = "Total vente"

# ==================== DÉTAIL JOURNÉE ====================

@admin.register(DetailJournee)
class DetailJourneeAdmin(admin.ModelAdmin):
    list_display = ['date', 'nombre_ventes', 'ca_display', 
                   'benefice_display', 'status_journee']
    list_filter = ['date']
    search_fields = ['date']
    inlines = [VenteInline]
    readonly_fields = ['resume_financier', 'created_at', 'updated_at']
    filter_horizontal = ['employes']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Frais Fixes', {
            'fields': ('frais_local', 'frais_electricite_impots'),
        }),
        ('Employés', {
            'fields': ('employes',),
        }),
        ('Résumé Financier', {
            'fields': ('resume_financier',),
            'classes': ('wide',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_ventes(self, obj):
        count = obj.vente_set.count()
        return f"{count} vente(s)"
    nombre_ventes.short_description = "Ventes"
    
    def ca_display(self, obj):
        return format_html(
            '<span style="color: #28a745;">{} DA</span>',
            round(obj.chiffre_affaire, 2)
        )
    ca_display.short_description = "Chiffre d'affaires"
    ca_display.admin_order_field = 'chiffre_affaire'  # Note: c'est une propriété, pas un champ
    
    def benefice_display(self, obj):
        benefice = obj.benefice
        if benefice >= 0:
            color = '#28a745'
            icon = '📈'
        else:
            color = '#dc3545'
            icon = '📉'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {} DA</span>',
            color, icon, round(benefice, 2)
        )
    benefice_display.short_description = "Bénéfice"
    
    def status_journee(self, obj):
        from datetime import date

        if obj.date == date.today():
            return mark_safe(
                '<span style="background: #ffc107; color: black; padding: 5px 10px; border-radius: 15px;">Aujourd\'hui</span>'
            )

        elif obj.date < date.today():
            return mark_safe(
                '<span style="background: #28a745; color: white; padding: 5px 10px; border-radius: 15px;">Terminée</span>'
            )

        else:
            return mark_safe(
                '<span style="background: #17a2b8; color: white; padding: 5px 10px; border-radius: 15px;">Future</span>'
            )
    
    def resume_financier(self, obj):
        if not obj.pk:
            return "Enregistrez d'abord la journée"
        
        return format_html(
            '''
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 20px; border-radius: 10px;">
                <h3 style="margin-top: 0;">📊 Résumé Financier</h3>
                <table style="width: 100%; color: white;">
                    <tr>
                        <td>💰 Chiffre d'affaires :</td>
                        <td style="text-align: right; font-weight: bold;">{ca} DA</td>
                    </tr>
                    <tr>
                        <td>📦 Frais ingrédients :</td>
                        <td style="text-align: right;">{frais_ingredients} DA</td>
                    </tr>
                    <tr>
                        <td>🎁 Frais emballage :</td>
                        <td style="text-align: right;">{frais_emballage} DA</td>
                    </tr>
                    <tr>
                        <td>🏠 Frais local :</td>
                        <td style="text-align: right;">{frais_local} DA</td>
                    </tr>
                    <tr>
                        <td>⚡ Électricité & Impôts :</td>
                        <td style="text-align: right;">{frais_elec} DA</td>
                    </tr>
                    <tr>
                        <td>👥 Salaires :</td>
                        <td style="text-align: right;">{salaires} DA</td>
                    </tr>
                    <tr style="border-top: 2px solid white;">
                        <td><strong>💎 BÉNÉFICE NET :</strong></td>
                        <td style="text-align: right; font-size: 1.3em; font-weight: bold;">{benefice} DA</td>
                    </tr>
                </table>
            </div>
            ''',
            ca=round(obj.chiffre_affaire, 2),
            frais_ingredients=round(obj.total_frais_ingredients, 2),
            frais_emballage=round(obj.total_frais_emballage, 2),
            frais_local=round(obj.frais_local, 2),
            frais_elec=round(obj.frais_electricite_impots, 2),
            salaires=round(obj.total_salaires, 2),
            benefice=round(obj.benefice, 2)
        )
    resume_financier.short_description = "Résumé Financier"

# ==================== PERSONNALISATION ====================

admin.site.site_header = "🍰 Administration YounYami Pâtisserie"
admin.site.site_title = "YounYami Admin"
admin.site.index_title = "Tableau de Bord YounYami"