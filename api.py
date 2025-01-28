from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import mysql.connector

# Initialisation de l'application FastAPI
app = FastAPI()

# Configuration de la base de données MySQL
DB_CONFIG = {
    "host": "localhost", 
    "port": "3307", # Remplacez par l'adresse de votre serveur MySQL
    "user": "root",       # Remplacez par votre nom d'utilisateur MySQL
    "password": "example",      # Remplacez par votre mot de passe MySQL
    "database": "pettitzoo"
}

# Modèle pour les entrées
class Animal(BaseModel):
    nom: str
    description: str
    image: str
    decors: str

# Connexion à la base de données
def get_db_connection():
    connect = mysql.connector.connect(**DB_CONFIG)
    cursor = connect.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS `animaux` (
                `id` int NOT NULL AUTO_INCREMENT,
                `nom` varchar(250) NOT NULL,
                `description` text NOT NULL,
                `image` varchar(250) NOT NULL,
                `decor` varchar(250) NOT NULL,
                PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                   """)


    return connect

# Endpoint : teste le démarrage de l'API
@app.get("/")
def test_demarrage():
    return {"serveur" : "démarré"}

# Endpoint : Liste de tous les noms d'animaux
@app.get("/animaux/noms")
def get_all_animal_names():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT nom FROM animaux")
    noms = cursor.fetchall()
    connection.close()
    return [nom[0] for nom in noms]

# Endpoint : Toutes les données d'un animal suivant son ID
@app.get("/animaux/{animal_id}")
def get_animal_by_id(animal_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM animaux WHERE id = %s", (animal_id,))
    animal = cursor.fetchone()
    connection.close()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    return animal

# Endpoint : Ajout d'un nouvel animal
@app.post("/animaux")
def add_animal(animal: Animal):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO animaux (nom, description, image, decors) VALUES (%s, %s, %s, %s)",
        (animal.nom, animal.description, animal.image, animal.decors)
    )
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()
    return {"id": new_id, "message": "Animal ajouté avec succès"}

# Endpoint : Supprimer un animal suivant son ID
@app.delete("/animaux/{animal_id}")
def delete_animal(animal_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM animaux WHERE id = %s", (animal_id,))
    connection.commit()
    affected_rows = cursor.rowcount
    connection.close()
    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="Animal non trouvé")
    return {"message": "Animal supprimé avec succès"}
