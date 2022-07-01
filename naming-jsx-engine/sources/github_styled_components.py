from github import Github
g = Github("access_token")

repo = "styled-components/styled-components"
tags = "styled-components"
# get all repositories with dependency "styled-components" - which the id is "UGFja2FnZS01MDYyMTAyMzk="
# https://github.com/styled-components/styled-components/network/dependents?package_id=UGFja2FnZS01MDYyMTAyMzk%3D
