import os

def build_env():
    base_dir = "assets/data_366"
    os.makedirs(base_dir, exist_ok=True)

    donations_content = """Juan Perez - $500 - Para la iglesia
Maria Gonzalez : 200 dolores (2023-10-01)
Carlos Santana gave 1500
Lupe - $300 gracias
Ignacio "Nacho" Varga | 450
Hector Salamanca ::: 800.50 pesos? No, dollars.
Lalo : $ 1200
Gus Fring gave $5000 for the roof
Tuco: 100
"""
    
    with open(os.path.join(base_dir, "donations_log.txt"), "w", encoding="utf-8") as f:
        f.write(donations_content)

    music_requests_content = """Song: Cielito Lindo | Genre: Mariachi | Requested by: Maria
Song: Despacito | Genre: Pop | Requested by: Luis
Song: El Rey | Genre: Ranchera | Requested by: Alejandro
Song: La Chona | Genre: Norteño | Requested by: Pepe
Song: Shape of You | Genre: Pop | Requested by: Kevin
Song: El Sinaloense | Genre: Banda | Requested by: Juan
Song: Tití Me Preguntó | Genre: Reggaeton | Requested by: Carlos
Song: Volver Volver | Genre: Ranchera | Requested by: Lupe
Song: Caminos de Michoacán | Genre: Norteño | Requested by: Lalo
Song: Hotel California | Genre: Rock | Requested by: Diego
"""

    with open(os.path.join(base_dir, "music_requests.txt"), "w", encoding="utf-8") as f:
        f.write(music_requests_content)

if __name__ == "__main__":
    build_env()
