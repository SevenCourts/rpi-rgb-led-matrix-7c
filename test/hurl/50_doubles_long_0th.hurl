POST {{tableau_server_url}}/score/xyz
Content-Type: application/json
{"client-id":"hurl-test",
"target-panels":["{{7c_target_panel}}"],
"isDoubles":true,
"isTeamEvent":false,
"t1name":"M.González/I.Shinkarenko",
"t2name":"F.Portis/D.Shapovalov-Lukjanenko",
"t1":{"p1":{"colors":"","firstname":"Mario","flag":"","lastname":"González"},"p2":{"colors":"","firstname":"Ilya","flag":"","lastname":"Shinkarenko"}},
"t2":{"p1":{"colors":"","firstname":"Freddy","flag":"","lastname":"Portis"},"p2":{"colors":"","firstname":"Dymytro","flag":"","lastname":"Shapovalov-Lukjanenko"}},
"t1serves":null,
"setScores":[],
"gameScore":{"first":"0","second":"0"},
"matchStatus":"IN_GAME"}