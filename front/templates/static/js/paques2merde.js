$(document).ready(function() {
        console.log("bouffon")
        if (document.getElementById('joli_titre')) {
            new CircleType(document.getElementById('joli_titre')).radius(524);
        }
        var alea = getRandomIntInclusive(1, 5)
        load_video(alea)
        setTimeout(function() { $(".retour").removeAttr("hidden") }, 10000);
        console.log("genius");
        $(".retour").on("click", function() {
            window.history.back();
        })
        if (document.location == "accueil") {
            var count = $('#nb_points').attr("class")

            setTimeout(function() {
                odometer.innerHTML = count;
            }, 1000);

            var count2 = $('#nb_qr').attr("class")
            setTimeout(function() {
                odometer1.innerHTML = count2;
            }, 1000);
        }
        $(".button").on("click", function() {
            alert("commande validée")
        })
    })
    // function($) { "use strict";

$(function() {
    var header = $(".start-style");
    $(window).scroll(function() {
        var scroll = $(window).scrollTop();

        if (scroll >= 10) {
            header.removeClass('start-style').addClass("scroll-on");
        } else {
            header.removeClass("scroll-on").addClass('start-style');
        }
    });
});

//Animation

$(document).ready(function() {
    $('body.hero-anime').removeClass('hero-anime');
});

//Menu On Hover
function getRandomIntInclusive(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
$('body').on('mouseenter mouseleave', '.nav-item', function(e) {
    if ($(window).width() > 750) {
        var _d = $(e.target).closest('.nav-item');
        _d.addClass('show');
        setTimeout(function() {
            _d[_d.is(':hover') ? 'addClass' : 'removeClass']('show');
        }, 1);
    }
});

//Switch light/dark

$("#switch").on('click', function() {
    if ($("body").hasClass("dark")) {
        $("body").removeClass("dark");
        $("#switch").removeClass("switched");
    } else {
        $("body").addClass("dark");
        $("#switch").addClass("switched");
    }
});

function load_video(i) {
    var video = "#" + i
    console.log(video)
    $(video).removeAttr("hidden")
}