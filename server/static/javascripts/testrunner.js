window._timers = {};

function timeStart(obj) {
    window._timers[obj] = null;            
    window._timers[obj] = (new Date).getTime();
}

function timeEnd(obj) {
    if (window._timers[obj]) {
        var diff = (new Date).getTime() - window._timers[obj];
        window._timers[obj] = null;            
        return diff;
    }
    return null;
}

window.users = null;
window.user_visits = null;
window.clicktrail = null;
window.jikan = null;
window.currentClick = null;

function runTestWithUsers(users) {
    window.users = users;
    if (advanceTest()) {
        runtest();
    }
}

function advanceTest() {
    if ((window.clicktrail == null) || (window.clicktrail.length == 0)) {
        // We're done with this particular visit. Try to bump the user
        if ((window.user_visits == null) || (window.user_visits.length == 0)) {
            // We're done with this particular user
            if ((window.users == null) || (window.users.length == 0)) {
                // We're done with the whole test!
                alert("Test Finished!");
                return false;
            }
            else {
                advanceUser();
                advanceVisit();
                advanceClick();
                return true;
            }
        }
        else {
            // We're still going with this user
            advanceVisit();
            advanceClick();
            return true;
        }
    }
    else {
        advanceClick();
        return true;
    }
}

function advanceUser() {
    ClearDb();
    window.user_visits = window.users.shift(); 
}

function advanceVisit() {
    var visit = window.user_visits.shift();
    window.clicktrail = visit["clicktrail"];
    window.jikan = visit["time"];
}

function advanceClick() {
    var nextClick = window.clicktrail.shift();
    window.currentClick = nextClick + "?now=" + window.jikan;
}

function runtest() {
    $("#testcontainer").html('<iframe id="testframe" style="width: 100%; height: 500px; border: 4px solid #333;"></iframe>');
    timeStart('load');
    $('iframe#testframe').attr('src', window.currentClick);
}

function LogData(url, params, dataFetch, dataLoad, templateParse) {
    var diff = timeEnd('load');
	$("#results").append("<tr><td>" + url + "</td><td>" + params + "</td><td>" + diff + "</td><td>" + dataFetch + "</td><td>" + dataLoad + "</td><td>" + templateParse + "</td></tr>");
    if (advanceTest()) {
        window.setTimeout('runtest()', 1000);
    }   
}

function ClearDb() {
    $('iframe#testframe').contents().find('#clearButton').each(function(i) {         
        this.click();
    });
}
