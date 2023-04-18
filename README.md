# Programming Assignment 2
Final Project for Computer Networks

**Commands**
Note: "" in usage denotes that the argument MUST be wrapped by quotes.

Connect: default is localhost:25565.
%connect [IP address]

Join: join the public group 
%join [username]

Post: add a post to the public group
%post "[topic]" "[body]"

Leave: leave the public group
%leave

Message: get message from id
%message [id]

Exit: disconnect from server
%exit

Groups: get listing of private groups (pre-made)
%groups

Join Group: join private group by id/name w/ username
%groupjoin [groupid | "groupname"] "[username]"

Group Post: post message in private group
%grouppost [groupid | "groupname"] "[topic]" "[message]"

Group Users: get users in private group (note that quotations NOT used)
%groupusers [groupid | groupname]

Group Leave: leave private group
%groupleave [groupid | groupname]

Group Message: get private group message from id
%groupmessage [groupid | "groupname"] [message_id]
