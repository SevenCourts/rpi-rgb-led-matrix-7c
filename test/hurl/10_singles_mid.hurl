POST {{tableau_server_url}}/score/xyz
Content-Type: application/json
{"client-id":"hurl-test",
"target-panels":["{{7c_target_panel}}"],
"isDoubles":false, 
"isTeamEvent":false,
"t1name":"R.Federer",
"t2name":"E.Gulbis",
"t1":{"p1":{"colors":"","firstname":"Roger","flag":"","lastname":"Federer"}},
"t2":{"p1":{"colors":"","firstname":"Ernests","flag":"","lastname":"Gulbis"}},
"t1serves":true,
"setScores":[{"first":2,"second":0}],
"gameScore":{"first":"40","second":"0"},
"matchStatus":"IN_GAME",
"description":"","authorName":"test","appVersion":"hurl-test","date":1672413885887,"userPlan":"FREE",
"appOS":"Android","matchCreationDate":1672402758432}