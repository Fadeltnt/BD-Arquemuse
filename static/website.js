const hamMenu = document.querySelector(".ham-menu");

const offScreenMenu = document.querySelector(".off-screen-menu");

hamMenu.addEventListener("click", () => {
  hamMenu.classList.toggle("active");
  offScreenMenu.classList.toggle("active");
});

// Fonction pour récupérer les données des cours depuis le serveur
function getCoursesData() {
    fetch('/courses') // Remplacez '/get_courses_data' par l'URL de votre route Flask
        .then(response => response.json())
        .then(data => {
            // Une fois les données récupérées, appelez une fonction pour les afficher dans l'emploi du temps
            displayCourses(data);
        })
        .catch(error => console.error('Erreur lors de la récupération des données des cours:', error));
}

// Fonction pour afficher les données des cours dans l'emploi du temps
function displayCourses(coursesData) {
    const tableBody = document.querySelector('tbody');

    // Efface le contenu actuel de la table
    tableBody.innerHTML = '';

    // Boucle à travers les données des cours et les ajoute à la table
    coursesData.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${course.date}</td>
            <td>${course.jour}</td>
            <td>${course.heure}</td>
            <td>${course.duree}</td>
            <td>${course.instrument}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Appeler la fonction pour récupérer et afficher les données des cours lors du chargement de la page
document.addEventListener('DOMContentLoaded', getCoursesData);


document.getElementById("availability-form").addEventListener("submit", function(event) {
    event.preventDefault(); // Empêche le formulaire de se soumettre normalement

    // Récupérer les valeurs du formulaire
    var day = document.getElementById("day").value;
    var startTime = document.getElementById("start-time").value;
    var endTime = document.getElementById("end-time").value;


    console.log("Jour:", day);
    console.log("Heure de début:", startTime);
    console.log("Heure de fin:", endTime);

    // Réinitialiser le formulaire si nécessaire
    // this.reset();
});

