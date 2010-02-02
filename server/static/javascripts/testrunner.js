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

window.dataSources = [
["/static/javascripts/userLoad1.js","Testing Run"],
// ["/static/wiki1/traditional_1_a.js","Wiki Test 1(a) - Traditional Hosting"],
// ["/static/wiki1/tokyo_1_a.js","Wiki Test 1(a) - Flying Templates"],
// ["/static/wiki1/synckit_1_a.js","Wiki Test 1(a) - Sync Kit"],
// ["/static/wiki2/traditional_1_b.js","Wiki Test 1(b) - Traditional Hosting"],
// ["/static/wiki2/tokyo_1_b.js","Wiki Test 1(b) - Flying Templates"],
// ["/static/wiki2/synckit_1_b.js","Wiki Test 1(b) - Sync Kit"],
// ["/static/wiki3/traditional_1_c.js","Wiki Test 1(c) - Traditional Hosting"],
// ["/static/wiki3/tokyo_1_c.js","Wiki Test 1(c) - Flying Templates"],
// ["/static/wiki3/synckit_1_c.js","Wiki Test 1(c) - Sync Kit"],
// ["/static/blog1/traditional_2_a.js","Blog Test 2(a) - Traditional Hosting"],
// ["/static/blog1/tokyo_2_a.js","Blog Test 2(a) - Flying Templates"],
// ["/static/blog1/synckit_2_a.js","Blog Test 2(a) - Sync Kit"],
// ["/static/test_dom/testdom.js","Test DOM Load and JS Startup"]
];

window.users = null;
window.user_visits = null;
window.clicktrail = null;
window.currentDataSource = -1;
window.jikan = null;
window.currentClick = null;
window.userNum = 0;
window.visitNum = 0;

function runTestWithUsers(users) {
    window.users = users;
    if (advanceTest()) {
        runtest();
    }
    else {
        // Go to next test file
    }
}

function advanceTest() {
    if ((window.clicktrail == null) || (window.clicktrail.length == 0)) {
        // We're done with this particular visit. Try to bump the user
        if ((window.user_visits == null) || (window.user_visits.length == 0)) {
            // We're done with this particular user
            if ((window.users == null) || (window.users.length == 0)) {
                // We're done with this test file
                if (window.currentDataSource >= (window.dataSources.length - 1)) {
                    // We're done with the batch!
                    alert("Test Finished!");
                    return false;
                }
                else {
                    // Start new batch
                    advanceTestFile();
                }
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

function advanceTestFile() {
    window.currentDataSource = window.currentDataSource + 1;
    $.getScript(window.dataSources[window.currentDataSource][0]);	
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
    
    window.currentClick = window.currentClick.replace('html?', 'html#');
}

function runtest() {
    $("#testcontainer").html('<iframe id="testframe" name="testframe" style="width: 100%; height: 500px; border: 4px solid #333;"></iframe>');
    $("#debug").html('<p><b>Loading: ' + window.currentClick + '</b></p>');
    timeStart('load');
    $('iframe#testframe').attr('src', window.currentClick);
}

function LogData(page_name, style, url, params, synckit) {
    var diff = timeEnd('load');
    var dataFetch = synckit._dataTransferTime;
    var dataLoad = synckit._bulkloadTime;
    var templateParse = synckit._templateTime;

    var test_batch_name = $('#test_batch_name').val();
    var test_name = window.dataSources[window.currentDataSource][1];

    var latency = $('#latency').val();
    var bandwidth = $('#bandwidth').val();
    var test_file = $('#dsselect').val();
    var test_description = "ted";
    var user = window.userNum;
    var visit_number = window.visitNum;
    
    url = window.currentClick;
	$("#last_result").html("<td>" + style + "</td><td>" + url + "</td><td>" + params + "</td><td>" + diff + "</td><td>" + dataFetch + "</td><td>" + dataLoad + "</td><td>" + templateParse + "</td>");
    $.post("/clientlogger/log", {
        "test_batch_name":test_batch_name,
        "test_name":test_name,
        "page_name":page_name,
        "test_file":test_file,
        "test_style":style,
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
