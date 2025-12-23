import json
import random
from datetime import date, timedelta

# --- CONFIGURATION ---
ANNEE_DEBUT = 2026
FICHIER_SORTIE = "journal_musical_ULTIMATE.json"

# Liste globale
DATABASE = []

def add(artiste, album, genre, tag="Découverte"):
    """Ajoute un album à la liste s'il n'est pas déjà présent."""
    for entry in DATABASE:
        # Vérification stricte pour éviter les doublons
        if entry['artiste'] == artiste and entry['album'] == album:
            return 
    DATABASE.append({
        "artiste": artiste, "album": album, "genre": genre, "tag": tag,
        "ecoute": False, "note": None, "avis": ""
    })

def construire_bibliotheque():
    print("🏗️  Construction de la bibliothèque musicale (Mode 365 JOURS)...")

    # ==========================================================
    # 1. NOUVELLE GÉNÉRATION & AJOUTS RÉCENTS
    # ==========================================================
    for alb in ["KOLAF", "ERRR", "24"]: add("La Fève", alb, "Rap FR", "New Wave")
    for alb in ["Playboi Carti", "Die Lit", "Whole Lotta Red", "I AM MUSIC"]: add("Playboi Carti", alb, "Rap US", "Rage/Trap")
    for alb in ["dont smile at me", "WHEN WE ALL FALL ASLEEP, WHERE DO WE GO?", "Happier Than Ever", "HIT ME HARD AND SOFT"]: add("Billie Eilish", alb, "Pop Alt", "INTEGRALE")
    ts_albums = ["Taylor Swift", "Fearless (Taylor's Version)", "Speak Now (Taylor's Version)", "Red (Taylor's Version)", "1989 (Taylor's Version)", "reputation", "Lover", "folklore", "evermore", "Midnights", "The Tortured Poets Department"]
    for alb in ts_albums: add("Taylor Swift", alb, "Pop", "INTEGRALE")
    for alb in ["Yours Truly", "My Everything", "Dangerous Woman", "Sweetener", "thank u, next", "Positions", "eternal sunshine"]: add("Ariana Grande", alb, "Pop", "INTEGRALE")

    # ==========================================================
    # 2. LÉGENDES SOUL / POP / FUNK
    # ==========================================================
    mj_albums = ["Off the Wall", "Thriller", "Bad", "Dangerous", "HIStory: Past, Present and Future, Book I", "Invincible", "Xscape"]
    for alb in mj_albums: add("Michael Jackson", alb, "Pop/Soul", "Légende")
    sw_albums = ["Music of My Mind", "Talking Book", "Innervisions", "Fulfillingness' First Finale", "Songs in the Key of Life", "Hotter than July"]
    for alb in sw_albums: add("Stevie Wonder", alb, "Soul", "Légende")
    prince_albums = ["For You", "Prince", "Dirty Mind", "Controversy", "1999", "Purple Rain", "Around the World in a Day", "Parade", "Sign o' the Times", "Diamonds and Pearls", "Musicology"]
    for alb in prince_albums: add("Prince", alb, "Pop/Funk", "INTEGRALE")
    beegees_albums = ["Main Course", "Children of the World", "Saturday Night Fever", "Spirits Having Flown", "Living Eyes", "E.S.P.", "One"]
    for alb in beegees_albums: add("The Bee Gees", alb, "Disco/Pop", "INTEGRALE")

    # ==========================================================
    # 3. ELECTRO & ROCK
    # ==========================================================
    dp_albums = ["Homework", "Discovery", "Human After All", "Random Access Memories", "Alive 1997", "Alive 2007", "Tron: Legacy"]
    for alb in dp_albums: add("Daft Punk", alb, "Electro", "INTEGRALE")
    pf_albums = ["The Piper at the Gates of Dawn", "A Saucerful of Secrets", "More", "Ummagumma", "Atom Heart Mother", "Meddle", "Obscured by Clouds", "The Dark Side of the Moon", "Wish You Were Here", "Animals", "The Wall", "The Final Cut", "A Momentary Lapse of Reason", "The Division Bell", "The Endless River"]
    for alb in pf_albums: add("Pink Floyd", alb, "Rock Prog", "INTEGRALE")
    beatles_albums = ["Please Please Me", "With the Beatles", "A Hard Day's Night", "Beatles for Sale", "Help!", "Rubber Soul", "Revolver", "Sgt. Pepper's Lonely Hearts Club Band", "Magical Mystery Tour", "The Beatles (White Album)", "Yellow Submarine", "Abbey Road", "Let It Be"]
    for alb in beatles_albums: add("The Beatles", alb, "Rock", "INTEGRALE")
    for alb in ["Innerspeaker", "Lonerism", "Currents", "The Slow Rush"]: add("Tame Impala", alb, "Psych Rock", "INTEGRALE")

    # ==========================================================
    # 4. RAP US & LATIN : INTEGRALES
    # ==========================================================
    bb_albums = ["X 100PRE", "YHLQMDLG", "Las que no iban a salir", "El Último Tour Del Mundo", "Un Verano Sin Ti", "Nadie Sabe Lo Que Va a Pasar Mañana"]
    for alb in bb_albums: add("Bad Bunny", alb, "Latin/Trap", "INTEGRALE")
    for alb in ["Por Vida", "Isolation", "Sin Miedo", "Red Moon In Venus", "Orquídeas", "Sincerely"]: add("Kali Uchis", alb, "Latin/Soul", "INTEGRALE")
    for alb in ["Bastard", "Goblin", "Wolf", "Cherry Bomb", "Flower Boy", "IGOR", "Call Me If You Get Lost", "Chromakopia"]: add("Tyler, The Creator", alb, "Rap US", "INTEGRALE")
    for alb in ["Section.80", "good kid, m.A.A.d city", "To Pimp A Butterfly", "untitled unmastered.", "DAMN.", "Mr. Morale & The Big Steppers", "GNX"]: add("Kendrick Lamar", alb, "Rap US", "INTEGRALE")
    for alb in ["The College Dropout", "Late Registration", "Graduation", "808s & Heartbreak", "My Beautiful Dark Twisted Fantasy", "Yeezus", "The Life of Pablo", "Ye", "Donda", "Vultures 1", "Vultures 2"]: add("Kanye West", alb, "Rap US", "INTEGRALE")
    for alb in ["Reasonable Doubt", "In My Lifetime, Vol. 1", "Vol. 2... Hard Knock Life", "Vol. 3... Life and Times of S. Carter", "The Dynasty", "The Blueprint", "The Black Album", "American Gangster", "The Blueprint 3", "4:44"]: add("Jay-Z", alb, "Rap US", "INTEGRALE")
    for alb in ["Doggystyle", "Tha Doggfather", "Da Game Is to Be Sold...", "No Limit Top Dogg", "Tha Last Meal", "Paid tha Cost to Be da Boss", "R&G", "Tha Blue Carpet Treatment", "Bush", "BODR", "Missionary"]: add("Snoop Dogg", alb, "Rap US", "INTEGRALE")
    for alb in ["Thank Me Later", "Take Care", "Nothing Was the Same", "If You're Reading This It's Too Late", "Views", "More Life", "Scorpion", "Certified Lover Boy", "Her Loss", "For All The Dogs"]: add("Drake", alb, "Rap US", "INTEGRALE")
    for alb in ["Cole World", "Born Sinner", "2014 Forest Hills Drive", "4 Your Eyez Only", "KOD", "The Off-Season", "The Fall Off"]: add("J. Cole", alb, "Rap US", "INTEGRALE")
    for alb in ["Blue Slide Park", "Watching Movies with the Sound Off", "GO:OD AM", "The Divine Feminine", "Swimming", "Circles", "Faces"]: add("Mac Miller", alb, "Rap US", "INTEGRALE")
    for alb in ["Rodeo", "Birds in the Trap Sing McKnight", "ASTROWORLD", "Utopia"]: add("Travis Scott", alb, "Rap US", "INTEGRALE")
    for alb in ["LIVE.LOVE.A$AP", "LONG.LIVE.A$AP", "AT.LONG.LAST.A$AP", "Testing", "Don't Be Dumb"]: add("A$AP Rocky", alb, "Rap US", "INTEGRALE")
    for alb in ["The Never Story", "DiCaprio 2", "The Forever Story", "God Does Like Ugly"]: add("JID", alb, "Rap US", "INTEGRALE")
    for alb in ["Imperial", "TA13OO", "ZUU", "Melt My Eyez See Your Future", "King of the Mischievous South Vol. 2"]: add("Denzel Curry", alb, "Rap US", "INTEGRALE")

    # 2025 SPECIALS
    add("Clipse", "Let God Sort Em Out", "Rap US", "Nouveauté")
    add("Clipse", "Hell Hath No Fury", "Rap US", "Classique")
    add("Freddie Gibbs", "Alfredo 2", "Rap US", "Nouveauté")
    add("Freddie Gibbs", "Alfredo", "Rap US", "Chef d'oeuvre")
    add("Freddie Gibbs", "Piñata", "Rap US", "Classique")
    add("Freddie Gibbs", "Bandana", "Rap US", "Classique")

    # ==========================================================
    # 5. RAP FR : INTEGRALES
    # ==========================================================
    for alb in ["Alph Lauren", "Alph Lauren 2", "Alph Lauren 3", "UMLA", "don dada mixtape vol 1"]: add("Alpha Wann", alb, "Rap FR", "Technique")
    for alb in ["Feu", "Cyborg", "Les Étoiles Vagabondes", "Expansion"]: add("Nekfeu", alb, "Rap FR", "Classique")
    for alb in ["Mauvais Oeil (Lunatic)","Temps mort", "Panthéon", "Ouest Side", "0.9", "Lunatic", "Futur", "D.U.C", "Nero Nemesis", "Trône", "Ultra", "Ad Vitam Aeternam"]: add("Booba", alb, "Rap FR", "INTEGRALE")
    for alb in ["ZERO","Or Noir", "Or Noir Part II", "Le Bruit de mon âme", "Double Fuck", "Okou Gnakouri", "Dozo", "2.7.0", "SVR", "Day One"]: add("Kaaris", alb, "Rap FR", "INTEGRALE")
    for alb in ["Que La Famille", "Le Monde Chico", "Dans la légende", "Deux frères"]: add("PNL", alb, "Rap FR", "INTEGRALE")
    for alb in ["Batterie Faible", "Ipséité", "Lithopédion", "QALF infinity", "Vieux Sons", "J'ai Menti", "Beyah"]: add("Damso", alb, "Rap FR", "INTEGRALE")
    for alb in ["A7", "Anarchie", "Deo Favente", "JVLIVS", "Rooftop", "JVLIVS II", "autobahn", "Julius Prequel", "JVLIVS III"]: add("SCH", alb, "Rap FR", "INTEGRALE")
    for alb in ["1994", "Paradise", "Sincèrement"]: add("Hamza", alb, "Rap FR", "INTEGRALE")
    for alb in ["Trinity", "L'Étrange Histoire de Mr. Anderson"]: add("Laylow", alb, "Rap FR", "INTEGRALE")

    # ==========================================================
    # 6. POP / R&B : INTEGRALES
    # ==========================================================
    for alb in ["Trilogy", "Kiss Land", "Beauty Behind the Madness", "Starboy", "My Dear Melancholy,", "After Hours", "Dawn FM", "Hurry Up Tomorrow"]: add("The Weeknd", alb, "Pop/R&B", "INTEGRALE")
    for alb in ["Dangerously in Love", "B'Day", "I Am... Sasha Fierce", "4", "BEYONCÉ", "Lemonade", "RENAISSANCE", "COWBOY CARTER"]: add("Beyoncé", alb, "R&B/Pop", "INTEGRALE")
    for alb in ["Good Girl Gone Bad", "Rated R", "Loud", "Talk That Talk", "Unapologetic", "ANTI"]: add("Rihanna", alb, "Pop/R&B", "INTEGRALE")
    for alb in ["nostalgia, ultra", "Channel Orange", "Endless", "Blonde"]: add("Frank Ocean", alb, "R&B", "INTEGRALE")
    for alb in ["Z (EP)", "Ctrl", "SOS", "Lana"]: add("SZA", alb, "R&B", "INTEGRALE")

    # ==========================================================
    # 7. AFRO / AMAPIANO
    # ==========================================================
    for alb in ["L.I.F.E", "On a Spaceship", "Outside", "African Giant", "Twice As Tall", "Love, Damini", "I Told Them..."]: add("Burna Boy", alb, "Afro-Fusion", "INTEGRALE")
    
    afro_extended = [
        ("Wizkid", "Made in Lagos"), ("Wizkid", "Superstar"), ("Wizkid", "More Love, Less Ego"),
        ("Fela Kuti", "Zombie"), ("Fela Kuti", "Expensive Shit"), ("Fela Kuti", "Roforofo Fight"),
        ("Davido", "Timeless"), ("Davido", "A Good Time"),
        ("Rema", "Rave & Roses"), ("Rema", "HEIS"),
        ("Asake", "Mr. Money With The Vibe"), ("Asake", "Work Of Art"), ("Asake", "Lungu Boy"),
        ("Tyla", "TYLA"), ("Tems", "Born in the Wild"), ("Tems", "If Orange Was A Place"),
        ("Ayra Starr", "19 & Dangerous"), ("Ayra Starr", "The Year I Turned 21"),
        ("Omah Lay", "Boy Alone"), ("Fireboy DML", "Laughter, Tears & Goosebumps"),
        ("Uncle Waffles", "Red Dragon"), ("Fally Ipupa", "Tokooos"), ("Amaarae", "Fountain Baby")
    ]
    for art, alb in afro_extended: add(art, alb, "Afro/World", "Vibe Afro")

    # --- AJOUTS AFRO LÉGENDES (Pour compléter le quota) ---
    afro_legends = [
        ("Ali Farka Touré", "Talking Timbuktu", "Blues Malien"),
        ("Salif Keita", "Soro", "Mandingue"),
        ("Youssou N'Dour", "Immigrés", "Mbalax"),
        ("Orchestra Baobab", "Pirate's Choice", "Afro-Cubain"),
        ("Franco & TPOK Jazz", "Mario", "Rumba Congolaise"),
        ("Manu Dibango", "Soul Makossa", "Makossa"),
        ("Cesária Évora", "Miss Perfumado", "Morna"),
        ("Magic System", "1er Gaou", "Zouglou"),
        ("Koffi Olomidé", "Loi", "Ndombolo"),
        ("Angelique Kidjo", "Djin Djin", "Benin/World"),
        ("Miriam Makeba", "Pata Pata", "Jazz/Folk")
    ]
    for art, alb, g in afro_legends: add(art, alb, g, "Légende Afro")

    # ==========================================================
    # 8. CULTURE & DIVERS
    # ==========================================================
    culture_list = [
        ("Nas", "Illmatic"), ("Notorious B.I.G.", "Ready to Die"), ("Tupac", "All Eyez On Me"),
        ("Dr. Dre", "2001"), ("Wu-Tang Clan", "Enter the Wu-Tang"), ("OutKast", "Stankonia"),
        ("Lauryn Hill", "The Miseducation of Lauryn Hill"),
        ("Marvin Gaye", "What's Going On"), ("Amy Winehouse", "Back to Black"),
        ("Nirvana", "Nevermind"), ("Radiohead", "OK Computer"), ("Queen", "A Night at the Opera"),
        ("Fleetwood Mac", "Rumours"), ("Bob Marley", "Exodus"), ("Sade", "Diamond Life"),
        ("Justice", "Cross"), ("Gorillaz", "Demon Days"), ("Miles Davis", "Kind of Blue")
    ]
    for art, alb in culture_list: add(art, alb, "Classique", "Culture")

    # --- AJOUTS CULTURE CLASSICS (Pour atteindre 365) ---
    culture_additions = [
        ("Jimi Hendrix", "Are You Experienced", "Rock Psyche"),
        ("The Doors", "The Doors", "Rock Psyche"),
        ("Aretha Franklin", "I Never Loved a Man the Way I Love You", "Soul"),
        ("Etta James", "At Last!", "Soul"),
        ("Massive Attack", "Mezzanine", "Trip-Hop"),
        ("Portishead", "Dummy", "Trip-Hop"),
        ("De La Soul", "3 Feet High and Rising", "Rap US"),
        ("Mobb Deep", "The Infamous", "Rap US"),
        ("Joy Division", "Unknown Pleasures", "Post-Punk"),
        ("The Smiths", "The Queen Is Dead", "Rock Indé"),
        ("David Bowie", "The Rise and Fall of Ziggy Stardust", "Glam Rock"),
        ("Led Zeppelin", "Led Zeppelin IV", "Hard Rock"),
        ("Tracy Chapman", "Tracy Chapman", "Folk"),
        ("D'angelo", "Voodoo", "Neo-Soul")
    ]
    for art, alb, g in culture_additions: add(art, alb, g, "Culture Générale")


def generer_json_final():
    construire_bibliotheque()
    
    # Mélange aléatoire
    random.shuffle(DATABASE)
    
    # --- ON COUPE OU ON COMPLETE POUR AVOIR PILE 365 ---
    target_count = 365
    
    # Si on a plus de 365, on coupe
    if len(DATABASE) >= target_count:
        final_list = DATABASE[:target_count]
    else:
        # Si par miracle on a moins, on complète (peu probable avec les ajouts)
        final_list = DATABASE
        compteur = 1
        while len(final_list) < target_count:
            add(f"Journée Libre {compteur}", "Choisis un album !", "Joker", "Libre")
            compteur += 1
            final_list = DATABASE

    print(f"🎸 Nombre total d'albums sélectionnés : {len(final_list)}")
    
    # Création du planning
    planning = {}
    date_debut = date(ANNEE_DEBUT, 1, 1) # 1er Janvier 2026
    
    for i, item in enumerate(final_list):
        date_courante = date_debut + timedelta(days=i)
        planning[str(date_courante)] = item

    # Sauvegarde
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(planning, f, indent=4, ensure_ascii=False)
        
    date_fin = date_debut + timedelta(days=len(final_list)-1)
    
    print("-" * 50)
    print(f"✅ FICHIER GÉNÉRÉ : {FICHIER_SORTIE}")
    print(f"📅 DÉBUT : 1er Janvier {ANNEE_DEBUT}")
    print(f"🏁 FIN : {date_fin.strftime('%d %B %Y')}")
    print(f"💿 TOTAL : {len(final_list)} albums (Compte rond !)")
    print("-" * 50)

if __name__ == "__main__":
    generer_json_final()