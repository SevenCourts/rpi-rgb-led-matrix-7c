POST {{tableau_server_url}}/score/xyz
Content-Type: application/json
{"client-id":"hurl-test",
"target-panels":["{{7c_target_panel}}"],
"isDoubles":true,
"isTeamEvent":false,
"t1name":"M.Lopez/J.Carlos",
"t2name":"F.Portis/L.Jordan",
"t1":{"p1":{"colors":"","firstname":"Mario","flag":"","lastname":"Lopez"},"p2":{"colors":"","firstname":"Juan","flag":"","lastname":"Carlos"}},
"t2":{"p1":{"colors":"","firstname":"Freddy","flag":"","lastname":"Portis"},"p2":{"colors":"","firstname":"Lui","flag":"","lastname":"Jordan"}},
"t1serves":null,
"setScores":[{"first":6,"second":2}, {"first":5,"second":7}, {"first":4,"second":6}],
"gameScore":{},
"matchStatus":"FINISHED",
"matchResult":"T2_WON",
"description":"","authorName":"test","appVersion":"hurl-test","date":1672413885887,"userPlan":"FREE",
"appOS":"Android","matchCreationDate":1672402758432}