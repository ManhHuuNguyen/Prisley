var map, infoWindow, initialPos;
var field_markers = [];
var position_markers=[];
var team_names = [];

// $.ajax({
//     type: "POST",
//     url: "/home",
//     actionType: "getTeams",
//     dataType: "json",
//     success: function (returnData) {
//         team_names = returnData;
//     }
// });

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
                icon: "static/images/icons/field_icon.png",
                animation: google.maps.Animation.DROP
            });
            field_markers.push(place);
            google.maps.event.addListener(marker, 'click', function () {
                $.ajax({
                    type: "POST",
                    url: "/return_matchups",
                    data: {"field_id": place.field_id},
                    dataType: "json",
                    success: function (returnData){
                        document.getElementById("field-image").src= returnData["field_image"];
                        // pin unpin
                        if (returnData["is_pinned"]) {
                            document.getElementById("pin").className = "pin";
                        }
                        else {
                            document.getElementById("pin").className = "unpin";
                        }
                        document.getElementById("field_name").innerHTML = returnData["field_name"];
                        document.getElementById("field_hour").innerHTML = "Open: " + returnData["open_time"] + " Close: " + returnData["close_time"];
                        var appointmentInfo = document.getElementById("appointment-info");
                        var appointmentContent = document.getElementById("appointment-content");
                        if (appointmentContent){
                            appointmentInfo.removeChild(appointmentContent);
                        }
                        appointmentContent = document.createElement("ul");
                        appointmentContent.setAttribute("data-field-id", place.field_id);
                        appointmentInfo.appendChild(appointmentContent);
                        appointmentContent.id = "appointment-content";
                        for (var i= 0; i<returnData["match_ups"].length; i++){
                            var match_up = returnData["match_ups"][i];
                            var li = document.createElement("li");
                            appointmentContent.appendChild(li);
                            var divAvatar = document.createElement("div");
                            divAvatar.style = "display: inline-block; width: 10%;";
                            li.appendChild(divAvatar);
                            var avatar = document.createElement("img");
                            avatar.className = "avatar";
                            avatar.src = "/static/images/avatars/" + match_up["avatar"];
                            divAvatar.appendChild(avatar);
                            var div1 = document.createElement("div");
                            div1.style = "display: inline-block; height: 100%; width: 90%; float: right;";
                            li.appendChild(div1);
                            var div2 = document.createElement("div");
                            div2.style = "margin-bottom: 7px;";
                            div1.appendChild(div2);
                            var userName = document.createElement("span");
                            userName.className = "username highlight";
                            userName.innerHTML = match_up["username"];
                            div2.appendChild(userName);
                            var dot1 = document.createElement("span");
                            dot1.style = "color: darkslategray; margin-left: 5px; margin-right: 5px";
                            dot1.innerHTML = "&bull;";
                            div2.appendChild(dot1);
                            var team = document.createElement("span");
                            team.className = "team highlight";
                            team.innerHTML = "@" + match_up["team"];
                            div2.appendChild(team);
                            var dot2 = document.createElement("span");
                            dot2.style = "color: darkslategray; margin-left: 5px; margin-right: 5px";
                            dot2.innerHTML = "&bull;";
                            div2.appendChild(dot2);
                            var time = document.createElement("span");
                            var times = match_up["time"].split("-");
                            time.className = "time highlight";
                            time.innerHTML = times[0] + "h-" + times[1] + "h";
                            div2.appendChild(time);
                            var div3 = document.createElement("div");
                            div1.appendChild(div3);
                            var comment = document.createElement("div");
                            comment.className = "comment";
                            comment.innerHTML = match_up["comment"];
                            div3.appendChild(comment);
                            var div4 = document.createElement("div");
                            div4.style="margin-top: 8px;";
                            div3.appendChild(div4);
                            var joinButton = document.createElement("img");
                            if (match_up["is_joinned"]) {
                                joinButton.className = "joinButton join";
                            }
                            else{
                                joinButton.className = "joinButton unjoin";
                            }
                            joinButton.setAttribute("data-match-id", match_up["match_id"]);
                            joinButton.setAttribute("onclick", "join_unjoin(this)");

                            div4.appendChild(joinButton);
                            var requestNum = document.createElement("span");
                            requestNum.className = "requestNum";
                            requestNum.innerHTML = match_up["request_num"];
                            div4.appendChild(requestNum);
                        }
                    }
                });
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
    var li = ul.getElementsByTagName('li');
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
    var pinButton = document.getElementById("pin");
    var field_id = parseInt(document.getElementById("appointment-content").getAttribute("data-field-id"));
    if (pinButton.className == 'pin'){
        pinButton.className = 'unpin';
        $.ajax({
            type: "POST",
            url: "/home",
            data: {"field_id": field_id, "actionType": "pin", "action": "-"},
            success: function () {
                window.alert("You won't be bothered by this field anymore.");
            }
        });
    }
    else {
        pinButton.className = 'pin';
        $.ajax({
            type: "POST",
            url: "/home",
            data: {"field_id": field_id, "actionType": "pin", "action": "+"},
            success: function () {
                window.alert("You will be notified whenever there is a new matchup.");
            }
        });
    }
}

function join_unjoin(thisJoinButton){
    var requestNum = thisJoinButton.parentNode.getElementsByClassName("requestNum")[0];
    var id = parseInt(thisJoinButton.getAttribute("data-match-id"));
    if (thisJoinButton.className == 'joinButton join'){
        thisJoinButton.className = "joinButton unjoin";
        requestNum.innerHTML = parseInt(requestNum.innerHTML) - 1;
        $.ajax({
            type: "POST",
            url: "/home",
            data: {"match_id": id, "actionType": "join", "action": "-"}
        });
    }
    else{
        thisJoinButton.className = "joinButton join";
        requestNum.innerHTML = parseInt(requestNum.innerHTML) + 1;
        $.ajax({
            type: "POST",
            url: "/home",
            data: {"match_id": id, "actionType": "join", "action": "+"}
        });
    }
}