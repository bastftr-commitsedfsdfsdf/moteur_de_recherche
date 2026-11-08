// Récupération des éléments de la page (équivalent des widgets)
const formulaire = document.getElementById("formulaire");
const champMotsCles = document.getElementById("mots-cles");
const champNombre = document.getElementById("nb-articles");
const choixSource = document.getElementById("source");
const champAuteur = document.getElementById("auteur");
const champDebut = document.getElementById("date-debut");
const champFin = document.getElementById("date-fin");
const zoneResultats = document.getElementById("resultats");
const sidebar = document.getElementById("sidebar");

// Ouvrir / fermer la sidebar : on ajoute ou retire la classe CSS "ouverte"
document.getElementById("ouvrir-filtres").addEventListener("click", () => {
    sidebar.classList.add("ouverte");
});
document.getElementById("fermer-filtres").addEventListener("click", () => {
    sidebar.classList.remove("ouverte");
});

// Réinitialiser : on remet chaque filtre à vide ("" = filtre ignoré par le serveur)
document.getElementById("reinitialiser-filtres").addEventListener("click", () => {
    choixSource.value = "";
    champAuteur.value = "";
    champDebut.value = "";
    champFin.value = "";
});

// Clic sur « Rechercher » / « Appliquer » (ou touche Entrée) : équivalent de clique_bouton
formulaire.addEventListener("submit", async (event) => {
    event.preventDefault(); // empêche le rechargement de la page
    sidebar.classList.remove("ouverte"); // referme les filtres pour voir les résultats

    // Construit l'URL /api/search?q=...&n=...&source=... (les caractères spéciaux sont encodés)
    const parametres = new URLSearchParams({
        q: champMotsCles.value,
        n: champNombre.value,
        source: choixSource.value,
        auteur: champAuteur.value,
        debut: champDebut.value, // "" si aucune date choisie, sinon "2024-01-31"
        fin: champFin.value,
    });
    const reponse = await fetch(`/api/search?${parametres}`);
    const resultats = await reponse.json();
    afficherResultats(resultats);
});

function afficherResultats(resultats) {
    zoneResultats.replaceChildren(); // vide la zone (équivalent de clear_output)

    if (resultats.length === 0) {
        zoneResultats.textContent = "Aucun document trouvé.";
        return;
    }

    const tableau = document.createElement("table");

    // Ligne d'en-tête
    const entete = tableau.createTHead().insertRow();
    for (const nom of ["Score", "Source", "Titre", "Auteur(s)", "Date"]) {
        const cellule = document.createElement("th");
        cellule.textContent = nom;
        entete.appendChild(cellule);
    }

    // Une ligne par document trouvé
    const corps = tableau.createTBody();
    for (const doc of resultats) {
        const ligne = corps.insertRow();
        ligne.insertCell().textContent = doc.score;
        ligne.insertCell().textContent = doc.type;

        const lien = document.createElement("a");
        lien.href = doc.url;
        lien.textContent = doc.titre; // textContent : le titre n'est jamais interprété comme du HTML
        lien.target = "_blank";       // ouvre le document dans un nouvel onglet
        ligne.insertCell().appendChild(lien);

        ligne.insertCell().textContent = doc.auteurs;
        ligne.insertCell().textContent = doc.date;
    }

    zoneResultats.appendChild(tableau);
}
