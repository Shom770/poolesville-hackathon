// let map;

function initMap() {
    ranchcoord = { lat: 39.14301073317686, lng: -77.28753786693156 };

    map = new google.maps.Map(document.getElementById("map"), {
        center: ranchcoord,
        zoom: 15,
    });

    new google.maps.Marker({
        position: ranchcoord,
        map,
        title: "hello"
    });
}


//39.14301073317686, -77.28753786693156
//39.17327628031249, -77.14560603137863
// window.initMap = initMap;