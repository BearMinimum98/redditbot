__author__ = 'Kevin'
class Data:
	USERNAME = "RedditBot/q"
	PASSWORD = "Butts420"
	playerBlacklist = []
	diceRoll = '^[rR]oll 1[dD](([1-9])([0-9]?)+)(((?i)k|m)?) in (clan)'
	fax = '^!fax (.*?)( -hic-)?$'
	loveMe = '((?i)I love you)(!)?'
	helpMe = "^!help"
	pickup = "^!sexbot"
	snack = "^!botsnack"
	smack = "^!botsmack"
	optimal = "^!optimal"
	trigger = "^!trigger"
	customTriggerStart = "(?i)^!"
	customTriggers = {
		"iamcaptaindean": "More like, YouAreCaptainButt",
		"iamcaptainbutt": "More like, IamCaptainDea- wait a sec...",
		"dagger32304": "I'm not fat, I'm fluffy!"
	}
	kill = "^!kill (.*?)( -hic-)?"
	iq = "^!iq"
	sharknado = "(?i)^!sharknado"
	sendCarePackage = "(?i)^package (.*)$"
	carePackageWhitelist = [2434890, 2344873, 2210210, 2479004, 2469228, 2467167, 2383225, 197209, 498276, 725347, 2500079, 2441215, 2662313, 524291, 2473196]
	superUser = [2434890, 2167442, 2479004]
	adminPlus = [2210210, 2344873]; adminPlus.extend(superUser)
	modPlus = [2469228, 2467167];modPlus.extend(adminPlus)
	karmanautPlus = [2383225, 197209, 498276, 725347, 2500079, 2441215, 2662313, 524291, 2473196];karmanautPlus.extend(modPlus)
	clanBlacklist = [2288943]
	upgradeStatus = "^[0-9]{4}$"
	wang = "^((?i)wang( me)?(!)?)$"
	wangOther = "^((?i)wang) (.*)"
	arrow = "^((?i)arrow( me)?[\.\!\?]?)$"
	arrowOther = "^((?i)arrow) (.*)"
	parseFax = "FaxBot has copied a (.*) into your clan's Fax Machine"
	setFlag = "^!setflag ['\"](.*?)['\"] (.*?) (.*?)( -hic-)?$"
	getFlag = "^!getflag ['\"](.*?)['\"] (.*?)( -hic-)?$"
	setRank = "^!setrank (.*?) (.*?)( -hic-)?$"
	whitelist = "^!whitelist (.*?)( -hic-)?$"
	points = "^!clanpoints"
	ignoreMe = "^!ignoreme"
	executeCommand = "^!execute (.*?)( -hic-)?$"
	clanMemberBack = "^((?i)back( -hic-)?)$"
	clanMemberHi = "^((?i)(hello|hi|hiya|hello clan|hey clan|hey\, clan|hello all|hey|heya|hi y\'all|howdy|hai|yo|ahoy|g\'day|sup|\'sup|hi there)[\.\!\?]?( -hic-)?)$"
	clanMemberLeave = "^((?i)(i\'m out|bye|goodbye|gtg|later)[\?\.\!]?( -hic-)?)$"
	rigRoll = '^[rR]oll 1[dD](([1-9])([0-9]?)+)(((?i)k|m)?) in (clan) get (([1-9])([0-9]?)+)'
	WANG_LIMIT = 5
	helpText = '''Clan chat commands:
!help - Sends help on RedditBot to your inbox
!fax <monster> - faxes <monster>
!ignoreme - ignores all future commands and triggers from you. (See KevZho to undo)

!whitelist <playerID> - whitelists <playerID> (Karmanaut or above)

!setrank <playerID> <rankNumber> - Sets the rank of <playerID> to <rankNumber>. See KevZho for rank number info. (Mod or above)

!getflag "<playername>" <flagName> - gets the value of <flagName> of <playername> (Admins only)


PM commands:
wang - Slaps you with a wang
wang <playername> - Slaps <playername> with a wang

arrow - Hits you with a time's arrow
arrow <playername> - Hits <playername> with a time's arrow.

package <playername> - Sends a newbie package to <playername> (Karmanaut or above)


RANKS:
normal member: 0,
reddit mold: 1,
lurker: 6,
redditor: 5,
top comment: 12,
novelty account: 11,
approved poster: 2,
reddit gold: 3,
karmanaut: 9'''
	# TODO: Add in easter egg words
	noTriggers = ["COME AT ME BRO.", "Do you know what you're doing, {0}?", "I don't understand your question, {0}.", "Have we done this before, {0}?", "{0}, I don't like it when you touch me there...", "That doesn't sound very smart, {0}.", "I can't let you do that, {0}.", "No, you can't put {1} in your ear, {0}.", "Did someone say {1}?  Because I think I heard someone say {1}.", "/em eats the {1}", "/em destroys the porcelain {1}", "/em vomits at the mention of {1}", "Nice {1} {0} honey.", "Did you learn to type {1} on your own?", "LURK MOAR", "/em faxes a {1} right out the window.", "/em wonders if you defenestrate when you get a BSOD...", "{0} makes god weep when using {1}...", "I'm a bot, not a {1}, dammit!", "{1} awakens Cthulhu.  It's about 500 years too early, so try something else.", "{1} makes me very angry.", "{1}ing will keep you regular.", "Please put down the {1} before you hurt yourself, sir or madam.", "Eat my shorts, {0}.", "How can you have any {1} if you don't eat your meat?", "You're the {2} person to ask for a {1} today.  Still not gonna happen.", "The {1}s have large talons.", "All your {1} belong to me.", "RAW RAW FIGHT THE {1}.", "These are not the {1} you are looking for.", "What is {1}?  {0} don't hurt me.", "{0} makes John Wayne turn in his grave.", "{1} is so OP it makes {0} cry.", "{0} was a {1}.  Was a good friend of mine.", "In Soviet Russia, {1} triggers {0}.", "{1} will give you the shakes, man.", "{0} has 99 problems but {1} ain't one.", "lol so random {0}.", "{0} has spiked the punch.", "{0} does not pass go and does not collect 200 {1}es."]