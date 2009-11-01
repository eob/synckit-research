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
window.userNum = 0;
window.visitNum = 0;

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
    window.userNum = window.userNum + 1;
    window.visitNum = 0;
    window.user_visits = window.users.shift(); 
}

function advanceVisit() {
    var visit = window.user_visits.shift();
    window.clicktrail = visit["clicktrail"];
    window.jikan = visit["time"];
    window.visitNum = window.visitNum + 1;
}

function advanceClick() {
    var nextClick = window.clicktrail.shift();
    var latency = $('#latency').val();;
    var bandwidth = $('#bandwidth').val();;
    if (nextClick.indexOf('?') == -1) {
        // No ?
        window.currentClick = nextClick + "?now=" + window.jikan + "&latency=" + latency + "&bandwidth=" + bandwidth;
    }
    else {
        window.currentClick = nextClick + "&now=" + window.jikan + "&latency=" + latency + "&bandwidth=" + bandwidth;        
    }
    window.currentClick = window.currentClick.replace('?', '#');
}

function runtest() {
    $("#testcontainer").html('<iframe id="testframe" style="width: 100%; height: 500px; border: 4px solid #333;"></iframe>');
    $("#debug").html('<p><b>Loading: ' + window.currentClick + '</b></p>');
    timeStart('load');
    $('iframe#testframe').attr('src', window.currentClick);
}

function LogData(style, url, params, dataFetch, dataLoad, templateParse) {
    var diff = timeEnd('load');
    var tester = $('#tester').val();
    var tester_comments = $('#tester_comments').val();
    var latency = $('#latency').val();
    var bandwidth = $('#bandwidth').val();
    var test_file = $('#dsselect').val();
    var test_description = "ted";
    var user = window.userNum;
    var visit_number = window.visitNum;
    
    url = window.currentClick;
	$("#last_result").html("<td>" + style + "</td><td>" + url + "</td><td>" + params + "</td><td>" + diff + "</td><td>" + dataFetch + "</td><td>" + dataLoad + "</td><td>" + templateParse + "</td>");
    $.post("/clientlogger/log", {
        "tester":tester,
        "tester_comments":tester_comments,
        "test_file":test_file,
        "test_description":test_description,
        "style":style,
        "url":url,
        "params":params,
        "user":user,
        "visit_number":visit_number,
        "total_time_to_render":diff,
        "data_fetch":dataFetch,
        "data_bulkload":dataLoad,
        "latency":latency,
        "bandwidth":bandwidth,
        "template_parse":templateParse
    }, function(data) {
        if (advanceTest()) {
            window.setTimeout('runtest()', 800);
        }           
    });
}

function ClearDb() {
    $('iframe#testframe').contents().find('#clearButton').each(function(i) {         
        this.click();
    });
}
