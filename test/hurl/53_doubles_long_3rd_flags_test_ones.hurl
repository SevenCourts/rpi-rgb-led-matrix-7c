POST {{tableau_server_url}}/score/xyz
Content-Type: application/json
{"client-id":"hurl-test",
"target-panels":["{{7c_target_panel}}"],
"isDoubles":true,
"isTeamEvent":false,
"t1name":"M.González/I.Shinkarenko",
"t2name":"F.Portis/D.Shapovalov-Lukjanenko",
"t1":{"p1":{"colors":"","firstname":"Mario","flag":"vatican","lastname":"González"},"p2":{"colors":"","firstname":"Ilya","flag":"ukraine","lastname":"Shinkarenko"}},
"t2":{"p1":{"colors":"","firstname":"Freddy","flag":"argentina","lastname":"Portis"},"p2":{"colors":"","firstname":"Dymytro","flag":"ukraine","lastname":"Shapovalov-Lukjanenko"}},
"t1serves":true,
"setScores":[{"first":6,"second":1}, {"first":1,"second":4}, {"first":2,"second":1}],
"gameScore":{"first":"40","second":"A"},
"matchStatus":"IN_GAME",
"description":"","authorName":"test","appVersion":"hurl-test","date":1672413885887,"userPlan":"FREE",
"appOS":"Android","matchCreationDate":1672402758432}