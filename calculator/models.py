from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import hashlib
import secrets

class AccessCode(models.Model):
    """Code d'accès au site"""
    code_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_code(self, raw_code):
        salt = secrets.token_hex(16)
        self.code_hash = hashlib.sha256(
            (raw_code + salt).encode()
        ).hexdigest() + f":{salt}"
    
    def check_code(self, raw_code):
        try:
            hash_part, salt = self.code_hash.split(':')
            return hash_part == hashlib.sha256(
                (raw_code + salt).encode()
            ).hexdigest()
        except:
            return False
    
    @classmethod
    def get_current_code(cls):
        return cls.objects.first()
    
    def save(self, *args, **kwargs):
        if not self.pk and AccessCode.objects.exists():
            raise ValidationError("Un seul code d'accès est autorisé")
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Code d'accès"
        verbose_name_plural = "Code d'accès"

class Ingredient(models.Model):
    """Ingrédients pour les recettes"""
    nom = models.CharField(max_length=100)
    poids_gramme = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    prix_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    def prix_par_gramme(self):
        return self.prix_kg / 1000
    
    def __str__(self):
        return f"{self.nom} ({self.poids_gramme}g)"
    
    class Meta:
        verbose_name = "Ingrédient"
        ordering = ['nom']

class RecetteGateau(models.Model):
    """Recettes de gâteaux"""
    nom = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gateaux/', blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient, through='RecetteIngredient')
    frais_emballage_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    prix_vente_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    nombre_unites_resultantes = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    
    def calculer_prix_revient_unitaire(self):
        total_ingredients = sum(
            ri.ingredient.prix_par_gramme() * ri.quantite_gramme 
            for ri in self.recetteingredient_set.all()
        )
        return (total_ingredients / self.nombre_unites_resultantes) + self.frais_emballage_unitaire
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Recette de gâteau"
        ordering = ['nom']

class RecetteIngredient(models.Model):
    """Relation entre recette et ingrédient avec quantité"""
    recette = models.ForeignKey(RecetteGateau, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantite_gramme = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    class Meta:
        unique_together = ['recette', 'ingredient']
        verbose_name = "Ingrédient de recette"

class Employe(models.Model):
    """Employés pour la journée"""
    nom = models.CharField(max_length=100)
    salaire_journalier = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    def __str__(self):
        return f"{self.nom} - {self.salaire_journalier} DA"
    
    class Meta:
        verbose_name = "Employé"
        ordering = ['nom']

class DetailJournee(models.Model):
    """Détail d'une journée"""
    date = models.DateField(unique=True)
    frais_local = models.DecimalField(max_digits=10, decimal_places=2, default=350)
    frais_electricite_impots = models.DecimalField(max_digits=10, decimal_places=2, default=150)
    employes = models.ManyToManyField(Employe, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_salaires(self):
        return sum(emp.salaire_journalier for emp in self.employes.all())
    
    @property
    def total_ventes(self):
        return sum(vente.total_vente() for vente in self.vente_set.all())
    
    @property
    def total_frais_ingredients(self):
        return sum(vente.calculer_frais_ingredients() for vente in self.vente_set.all())
    
    @property
    def total_frais_emballage(self):
        return sum(vente.calculer_frais_emballage() for vente in self.vente_set.all())
    
    @property
    def total_frais_fixes(self):
        return self.frais_local + self.frais_electricite_impots + self.total_salaires
    
    @property
    def chiffre_affaire(self):
        return self.total_ventes
    
    @property
    def total_frais(self):
        return self.total_frais_ingredients + self.total_frais_emballage + self.total_frais_fixes
    
    @property
    def benefice(self):
        return self.chiffre_affaire - self.total_frais
    
    def __str__(self):
        return f"Journée du {self.date}"
    
    class Meta:
        verbose_name = "Détail journée"
        ordering = ['-date']

class Vente(models.Model):
    """Ventes de gâteaux pour une journée"""
    detail_journee = models.ForeignKey(DetailJournee, on_delete=models.CASCADE)
    recette_gateau = models.ForeignKey(RecetteGateau, on_delete=models.CASCADE)
    quantite_vendue = models.IntegerField(validators=[MinValueValidator(0)])
    
    def total_vente(self):
        return self.quantite_vendue * self.recette_gateau.prix_vente_unitaire
    
    def calculer_frais_ingredients(self):
        prix_revient = self.recette_gateau.calculer_prix_revient_unitaire() - self.recette_gateau.frais_emballage_unitaire
        return prix_revient * self.quantite_vendue
    
    def calculer_frais_emballage(self):
        return self.recette_gateau.frais_emballage_unitaire * self.quantite_vendue
    
    class Meta:
        verbose_name = "Vente"
        unique_together = ['detail_journee', 'recette_gateau']