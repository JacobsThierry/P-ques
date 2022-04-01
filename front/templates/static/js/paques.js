$(document).ready(function() {
    console.log("genius");
    if (document.getElementById('joli_titre')) {
        new CircleType(document.getElementById('joli_titre')).radius(294);
    }
    setTimeout(() => { $(".rabbit").attr("hidden", "true") }, 3010);
    // setTimeout(() => {  $(".rabbit").attr("hidden","false")}, 6000);

    $(".surprise").on("click", function() {
        alea = getRandomIntInclusive(0, 1)
        if (alea == 1) {
            document.location.href = '/video'
        }
    })
    $(".easter-animation").on("click", function() {
        document.location.href = '/accueil'
    })

});

function getRandomIntInclusive(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}