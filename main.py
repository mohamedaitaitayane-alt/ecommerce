import json
import os

# --- CONFIGURATION ET PERSISTANCE ---

FICHIER_PRODUITS = "products.json"
FICHIER_PANIER = "cart.json"

PRODUITS_PAR_DEFAUT = [
    {"id": 1, "nom": "Ordinateur Portable", "prix": 899.99, "stock": 5},
    {"id": 2, "nom": "Souris Sans Fil", "prix": 25.50, "stock": 15},
    {"id": 3, "nom": "Écran 24 Pouces", "prix": 149.00, "stock": 8},
    {"id": 4, "nom": "Clavier Mécanique", "prix": 79.90, "stock": 10}
]

def charger_donnees(fichier, donnees_par_defaut):
    """Charge les données d'un fichier JSON. Crée le fichier si absent."""
    if not os.path.exists(fichier):
        sauvegarder_donnees(fichier, donnees_par_defaut)
        return donnees_par_defaut
    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print(f"⚠️ Erreur de lecture de {fichier}. Réinitialisation.")
        return donnees_par_defaut

def sauvegarder_donnees(fichier, donnees):
    """Sauvegarde les données dans un fichier JSON."""
    try:
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
    except IOError:
        print(f"⚠️ Impossible de sauvegarder les données dans {fichier}.")

# --- FONCTIONS ROBUSTES DE SAISIE ---

def saisir_entier(message):
    """Force l'utilisateur à saisir un nombre entier valide."""
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("❌ Saisie invalide. Veuillez entrer un nombre entier.")

def saisir_flottant(message):
    """Force l'utilisateur à saisir un nombre décimal valide."""
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("❌ Saisie invalide. Veuillez entrer un prix correct (ex: 12.50).")

# --- FONCTIONNALITÉS DU LOGICIEL ---

def afficher_produits(produits):
    """Affiche la liste des produits disponibles."""
    print("\n--- PRODUITS DISPONIBLES ---")
    print(f"{'ID':<5} {'Nom':<25} {'Prix':<10} {'Stock':<5}")
    print("-" * 50)
    for p in produits:
        print(f"{p['id']:<5} {p['nom']:<25} {p['prix']:<10.2f} {p['stock']:<5}")
    print("-" * 50)

def ajouter_au_panier(produits, panier):
    """Ajoute un produit au panier et met à jour les stocks."""
    afficher_produits(produits)
    id_cible = saisir_entier("Entrez l'ID du produit à ajouter : ")
    
    # Recherche du produit
    produit = next((p for p in produits if p["id"] == id_cible), None)
    
    if not produit:
        print("❌ Produit introuvable.")
        return
        
    if produit["stock"] <= 0:
        print("❌ Ce produit est en rupture de stock.")
        return
        
    quantite = saisir_entier(f"Quantité souhaitée (Max {produit['stock']}) : ")
    if quantite <= 0:
        print("❌ La quantité doit être supérieure à 0.")
        return
    if quantite > produit["stock"]:
        print("❌ Stock insuffisant pour cette quantité.")
        return
        
    # Mise à jour du stock produit
    produit["stock"] -= quantite
    
    # Ajout ou mise à jour dans le panier
    article_panier = next((item for item in panier if item["id"] == id_cible), None)
    if article_panier:
        article_panier["quantite"] += quantite
    else:
        panier.append({
            "id": produit["id"],
            "nom": produit["nom"],
            "prix": produit["prix"],
            "quantite": quantite
        })
        
    print(f"✅ {quantite}x '{produit['nom']}' ajouté(s) au panier.")
    sauvegarder_donnees(FICHIER_PRODUITS, produits)
    sauvegarder_donnees(FICHIER_PANIER, panier)

def afficher_panier(panier):
    """Visualise le contenu du panier et calcule le total."""
    print("\n--- VOTRE PANIER ---")
    if not panier:
        print("Votre panier est vide.")
        return 0
        
    print(f"{'Nom':<25} {'Prix unitaire':<15} {'Quantité':<10} {'Sous-total':<10}")
    print("-" * 65)
    total = 0
    for item in panier:
        sous_total = item["prix"] * item["quantite"]
        total += sous_total
        print(f"{item['nom']:<25} {item['prix']:<15.2f} {item['quantite']:<10} {sous_total:<10.2f}")
    print("-" * 65)
    print(f"TOTAL À PAYER : {total:.2f} €")
    return total

def retirer_du_panier(produits, panier):
    """Retire un produit du panier et restitue le stock."""
    if not panier:
        print("\nVotre panier est vide. Rien à retirer.")
        return
        
    afficher_panier(panier)
    id_cible = saisir_entier("Entrez l'ID du produit à retirer (ou modifier) : ")
    
    article = next((item for item in panier if item["id"] == id_cible), None)
    if not article:
        print("❌ Ce produit n'est pas dans votre panier.")
        return
        
    quantite_a_retirer = saisir_entier(f"Quantité à retirer (Max {article['quantite']}) : ")
    if quantite_a_retirer <= 0:
        print("❌ La quantité doit être supérieure à 0.")
        return
    if quantite_a_retirer > article["quantite"]:
        print("❌ Vous ne pouvez pas retirer plus que la quantité dans le panier.")
        return
        
    # Restituer le stock au catalogue
    produit_catalogue = next(p for p in produits if p["id"] == id_cible)
    produit_catalogue["stock"] += quantite_a_retirer
    
    # Ajuster ou supprimer du panier
    if quantite_a_retirer == article["quantite"]:
        panier.remove(article)
    else:
        article["quantite"] -= quantite_a_retirer
        
    print("✅ Panier mis à jour.")
    sauvegarder_donnees(FICHIER_PRODUITS, produits)
    sauvegarder_donnees(FICHIER_PANIER, panier)

def valider_commande(panier):
    """Valide la commande et vide le panier."""
    if not panier:
        print("❌ Votre panier est vide. Impossible de passer commande.")
        return
        
    afficher_panier(panier)
    confirmation = input("\nVoulez-vous valider et payer votre commande ? (o/n) : ").strip().lower()
    if confirmation == 'o':
        print("\n🎉 Commande validée avec succès ! Merci pour votre achat.")
        panier.clear()  # On vide le panier
        sauvegarder_donnees(FICHIER_PANIER, panier)
    else:
        print("Commande annulée ou suspendue.")

def ajouter_produit_admin(produits):
    """Mode Admin : Permet d'injecter un nouveau produit dans le catalogue JSON."""
    print("\n--- AJOUT DE PRODUIT (ADMIN) ---")
    nom = input("Nom du nouveau produit : ").strip()
    if not nom:
        print("❌ Le nom ne peut pas être vide.")
        return
        
    prix = saisir_flottant("Prix du produit (€) : ")
    stock = saisir_entier("Stock initial : ")
    
    if prix <= 0 or stock < 0:
        print("❌ Le prix doit être supérieur à 0 et le stock positif ou nul.")
        return
        
    # Génération automatique d'un nouvel ID unique
    nouvel_id = max([p["id"] for p in produits], default=0) + 1
    
    produits.append({
        "id": nouvel_id,
        "nom": nom,
        "prix": prix,
        "stock": stock
    })
    
    print(f"✅ Produit '{nom}' ajouté au catalogue avec l'ID {nouvel_id}.")
    sauvegarder_donnees(FICHIER_PRODUITS, produits)

# --- BOUCLE PRINCIPALE ---

def menu_principal():
    # Initialisation / Chargement des données au démarrage
    produits = charger_donnees(FICHIER_PRODUITS, PRODUITS_PAR_DEFAUT)
    panier = charger_donnees(FICHIER_PANIER, [])

    while True:
        print("\n=============================")
        print("       M-COMMERCE MENU       ")
        print("=============================")
        print("1. Consulter les produits")
        print("2. Ajouter un produit au panier")
        print("3. Voir mon panier et le total")
        print("4. Retirer un produit du panier")
        print("5. Valider ma commande (Checkout)")
        print("6. Ajouter un produit (Admin)")
        print("7. Quitter le programme")
        print("=============================")
        
        choix = input("Votre choix (1-7) : ").strip()
        
        if choix == "1":
            afficher_produits(produits)
        elif choix == "2":
            ajouter_au_panier(produits, panier)
        elif choix == "3":
            afficher_panier(panier)
        elif choix == "4":
            retirer_du_panier(produits, panier)
        elif choix == "5":
            valider_commande(panier)
        elif choix == "6":
            ajouter_produit_admin(produits)
        elif choix == "7":
            print("Merci de votre visite, à bientôt !")
            break
        else:
            print("❌ Option invalide. Veuillez choisir un nombre entre 1 et 7.")

if __name__ == "__main__":
    menu_principal()