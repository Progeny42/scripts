# Setting up PiHole

First off, you will need to setup some Groups under Group Management. In my case, I have a group called `GF Devices`. The name doesn't matter much, just make it suitable for what devices you wish to block. Make sure the Status is Enabled once created.

Next up in the Clients tab, select the Clients which you wish to add to your new group. I have a Desktop, a tablet and a phone added to the `GF Devices` group using the Group Assignment. Note I also removed the group from `Default`.

Then finally setup the Domains to block. I'm using the following to block (among others), reddit. Add a `RegEx filter` such as `(\.|^)reddit\.com$` and add it to the Blacklist. Now assign the Domains to the Group you setup. Ensure to remove it from `Default` so it only applies to devices within your Group.

# Setting up a Script

I'm using a Python script which gets run by Cron every hour. I've provided the script on my GitHub [here](https://github.com/Progeny42/scripts/blob/main/pihole-schedule-blocking.py) (It may be a bit quick and dirty, but it works sufficiently :))

Add this to a suitable location (I'm using `/usr/local/bin`) and then edit the script. At the top of the file, there are a couple of variables. The `enableBlockTime` and `disableBlockTime` are the times in 24 hour format which the blocking will be scheduled for. Mine is set to between 9am and 4pm.

Next is the `domainsToBlock`. This should contain a list of strings of the Domains that you wish to be blocked on shedule. The names should contain or match the Domains entered in the PiHole Domains page. I have `facebook` and `tumblr` added to this list in the script. The script will query the `gravity.db` for all domains in the `domainlist` table where the `domain` is equal to one of the strings in the `domainsToBlock` list. So in my case, it will look for `facebook`, and find `(\.|^)facebook\.com$`.

Next on line 77, there is a condition which checks where the script should enable or disable blocking the domain. It compares the current time to the start and end scheduled times, and also in my case checks the day of the week. This script checks that it is a weekday (freedom at the weekends), but checking it is `<= 4` (Friday). Adjust this as desired, or remove the condition entirely for it to work daily.

And that's it for the script. It will evaulate whether the criteria for blocking is met, compare it against what PiHole is currently setup to do, and then make changes if necessary (this saves updating PiHole each time if the end result is the same). It commits the changes to the database, and then flushes the PiHole DNS cache so it will block the sites (note if your browser also caches the sites, I can't help you with that - that is down to the browser itself).

If all works well, you can run the script manually using `python3 /usr/local/bin/pihole-schedule-block.py` and it will give a little bit of output depending on whether you are within the blocking period, and whether the PiHole currently has the domain blocked or not. Run it, and then login to the PiHole GUI and check to see whether the domains are Enabled or Disabled under Group Management > Domains.

# Run the script on a Schedule

I'm running this script hourly, as I'm checking between 9am and 4pm, so only need a resolution of an hour, but it set it up as desired.

You will need to setup a crontab using sudo as your need elevated permissions in order to modify the `gravity.db` database.

I did the following:

`sudo crontab -e`

and added:

`0 * * * * python3 /usr/local/bin/pihole-schedule-block.py`

&#x200B;

Any feedback would be appreciated, and if you desire, make suggestions / improvements to the python script.