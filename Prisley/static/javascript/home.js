var map, infoWindow, initialPos;
var field_markers = [];
var position_markers=[];
var teams = [];

String.prototype.format = function() {
  str = this;
  for (k in arguments) {
    str = str.replace("{" + k + "}", arguments[k])
  }
  return str;
};

function initMap(){
    initialPos = {lat: 21.0278, lng: 105.8342};
    map = new google.maps.Map(document.getElementById('map'), {
        center: initialPos,
        zoom: 14,
        mapTypeControl: true,
        mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR, position: google.maps.ControlPosition.TOP_CENTER}
    });

    infoWindow = new google.maps.InfoWindow;
    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(function (position) {
            initialPos = {lat: position.coords.latitude, lng: position.coords.longitude};
            // pretend this is VN, delete later
            initialPos = {lat: 21.0278, lng: 105.8342};
            //-------------------------
            map.setCenter(initialPos);
            createMarker({lat:initialPos.lat, lng: initialPos.lng}, false, 0);
            $.ajax({
            type: "POST",
            url: "/return_fields",
            dataType: "json",
            success: function(returnData){
                for (var i = 0; i < returnData.length; i++){
                    createMarker(returnData[i], true, i*150);
                }
            }});
            // search box
            var searchBox = new google.maps.places.SearchBox(document.getElementById("search_box"));
            map.controls[google.maps.ControlPosition.TOP_LEFT].push(document.getElementById("search_box"));
            map.addListener('bounds_changed',function () {
                searchBox.setBounds(map.getBounds());
            });
            searchBox.addListener('places_changed', function () {
                var places = searchBox.getPlaces();
                if (places.length == 0){
                    return;
                }
                position_markers.forEach(function (marker) {
                    marker.setMap(null);
                });
                position_markers = [];
                var bounds = new google.maps.LatLngBounds();
                places.forEach(function (place) {
                    if (!place.geometry){
                        console.log("Returned place contains no geometry");
                        return;
                    }
                    createMarker(place.geometry.location, false, 0);
                    var service = new google.maps.places.PlacesService(map);
                    if (place.geometry.viewport){
                        bounds.union(place.geometry.viewport);
                    }
                    else{
                        bounds.extend(place.geometry.location);
                    }
                });
                map.fitBounds(bounds);
            });

        }, function () {
            handleLocationError(true, infoWindow, map.getCenter());
        });
    }
    else{
        handleLocationError(false, infoWindow, map.getCenter());
    }
}

function createMarker(place, customized, time) {
    setTimeout(function () {
        if (customized) {
            var marker = new google.maps.Marker({
                map: map,
                position: place,
                icon: "../static/images/icons/field_icon.png",
                animation: google.maps.Animation.DROP
            });
            field_markers.push(place);
            google.maps.event.addListener(marker, 'click', function () {
                window.location = "/home/" + place.field_id;
            });
        }
        else {
            position_markers.push(new google.maps.Marker({
                map: map,
                position: place,
                animation: google.maps.Animation.DROP
            }));
        }
    }, time);
}

function handleLocationError(browserHasGeoLocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeoLocation ? 'Error: The Geolocation service failed.' : 'Error: Your browser doesn\'t support geolocation.');
    infoWindow.open(map);
}

// button function
function onClickNotification(thisButton) {
    thisButton.style.backgroundImage = "url('/static/images/icons/notification_icon2.png')";
    document.getElementById("profile_icon").style.backgroundImage = "url('/static/images/icons/profile_icon.png')";
    document.getElementById("message_icon").style.backgroundImage = "url('/static/images/icons/message_icon.png')";
}

function onClickProfile(thisButton) {
    thisButton.style.backgroundImage = "url('/static/images/icons/profile_icon2.png')";
    document.getElementById("notification_icon").style.backgroundImage = "url('/static/images/icons/notification_icon.png')";
    document.getElementById("message_icon").style.backgroundImage = "url('/static/images/icons/message_icon.png')";
}

function onClickChat(thisButton) {
    thisButton.style.backgroundImage = "url('/static/images/icons/message_icon2.png')";
    document.getElementById("notification_icon").style.backgroundImage = "url('/static/images/icons/notification_icon.png')";
    document.getElementById("profile_icon").style.backgroundImage = "url('/static/images/icons/profile_icon.png')";
}

// to make a slideshow
function forwardPic(){
    var imageLink = document.getElementById("field-image").src;
    var list = imageLink.split("/");
    var imageName = Number(list[list.length-1].split(".")[0]);
    imageName += 1;
}
// to make a slideshow
function backwardPic(){
    var imageLink = document.getElementById("field-image").src;
    var list = imageLink.split("/");
    var imageName = Number(list[list.length-1].split(".")[0]);
    imageName -= 1;
}

function filterMatchUp() {
    var input = document.getElementById('matchup-filter');
    var filter = input.value.toUpperCase();
    var ul = document.getElementById("appointment-content");
    var li = ul.getElementsByClassName("matchup");
    for (var i=0; i<li.length; i++){
        var joinedString = (li[i].getElementsByClassName("username")[0].innerHTML + li[i].getElementsByClassName("team")[0].innerHTML + li[i].getElementsByClassName("time")[0].innerHTML).toUpperCase();
        if (joinedString.indexOf(filter) == -1){
            li[i].style.display = "none";
        }
        else {
            li[i].style.display = "block";
        }
    }
}

function pin_unpin(){
    console.log("Pin buttoned being clicked");
    var pinButton = document.getElementById("pin");
    var field_id = parseInt(document.getElementById("appointment-content").getAttribute("data-field-id"));
    if (pinButton.className == 'pin'){
        pinButton.className = 'unpin';
        $.ajax({
            type: "POST",
            url: "/home/" + field_id,
            data: {actionType: "pin", "action": "-"},
            success: function () {
                window.alert("You won't be bothered by this field anymore.");
            }
        });
    }
    else {
        pinButton.className = 'pin';
        $.ajax({
            type: "POST",
            url: "/home/" + field_id,
            data: {actionType: "pin", "action": "+"},
            success: function () {
                window.alert("You will be notified whenever there is a new matchup.");
            }
        });
    }
}

function join_unjoin(thisJoinButton){
    var requestNum = thisJoinButton.parentNode.getElementsByClassName("requestNum")[0];
    var field_id = parseInt(document.getElementById("appointment-content").getAttribute("data-field-id"));
    var match_id = parseInt(thisJoinButton.getAttribute("data-match-id"));
    var select = thisJoinButton.parentNode.getElementsByTagName("select")[0];
    var team_id = select.options[select.selectedIndex].value;
    if (thisJoinButton.className == 'joinButton join'){
        thisJoinButton.className = "joinButton unjoin";
        requestNum.innerHTML = parseInt(requestNum.innerHTML) - 1;
        $.ajax({
            type: "POST",
            url: "/home/" + field_id,
            data: {"match_id": match_id, "team_id": team_id, "actionType": "join", "action": "-"},
            dataType: "json",
            success: function (returnData) {
                if (returnData["isSuccess"]){
                    thisJoinButton.className = "joinButton unjoin";
                    requestNum.innerHTML = parseInt(requestNum.innerHTML) - 1;
                }
                else{
                    window.alert("You cannot request to join a match that your team created itself.");
                }
            }
        });
    }
    else{
        $.ajax({
            type: "POST",
            url: "/home/" + field_id,
            data: {"match_id": match_id, "team_id": team_id, "actionType": "join", "action": "+"},
            dataType: "json",
            success: function (returnData) {
                if (returnData["isSuccess"]){
                    thisJoinButton.className = "joinButton join";
                    requestNum.innerHTML = parseInt(requestNum.innerHTML) + 1;
                }
                else{
                    window.alert("You cannot request to join a match that your team created itself.");
                }
            }
        });
    }
}

function selectTeam(itself, match_id){
    var team_id = itself.options[itself.selectedIndex].value;
    var field_id = parseInt(document.getElementById("appointment-content").getAttribute("data-field-id"));
    $.ajax({
        type: "POST",
        url: "/home/" + field_id,
        data:{"team_id": team_id, "actionType": "changeSelect"},
        dataType: "json",
        success: function (returnData) {
            console.log(itself.getAttribute("data-match-id"));
            if (returnData["is_joined"]){
                $("[data-match-id={0}]".format(match_id))[0].className = "joinButton join";
            }
            else{
                $("[data-match-id={0}]".format(match_id))[0].className = "joinButton unjoin";
            }
        }
    });
}