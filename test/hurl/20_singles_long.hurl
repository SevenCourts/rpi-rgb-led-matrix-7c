POST {{tableau_server_url}}/score/xyz
Content-Type: application/json
{"client-id":"hurl-test",
"target-panels":["{{7c_target_panel}}"],
"isDoubles":false, 
"isTeamEvent":false,
"t1name":"",
"t2name":"",
"t1":{"p1":{"colors":"","firstname":"Ilya","flag":"","lastname":"Shinkarenko"}},
"t2":{"p1":{"colors":"","firstname":"Dymytro","flag":"","lastname":"Shapovalov-Lukjanenko"}},
"t1serves":true,
"setScores":[{"first":2,"second":0}],
"gameScore":{"first":"40","second":"0"},
"matchStatus":"IN_GAME",
"description":"","authorName":"test","appVersion":"hurl-test","date":1672413885887,"userPlan":"FREE",
"appOS":"Android","matchCreationDate":1672402758432}