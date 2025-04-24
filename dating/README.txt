Team 26

Pablo Simón Martín Sánchez (100475383)
César Álvarez-Cascos Hervias (100475191)
Alejandro Fonseca Ortés (100475353)

Logic and other considerations

In the HOMEPAGE view, only users that align with the logged-in user preferences are shown.
The logged-in user also aligns with prefereces of users shown in the HOMEPAGE view.
When the user clicks on the "Show all" button, preferences are not taken into account.
Users previously blocked or liked by the logged-in user are not shown, as they won't be relevant in this "discovery" view.
Users that have blocked the logged-in user are not shown, even if they meet the previous criteria, and their profile page/view is unreachable.


From the point of view of one user, liking and blocking other user is exclusive, so one option excludes the other. 
For a match to happen, the like relation between two users must be bidirectional: user1 likes user2 and user2 likes user1.
Blocking users that likes you is allowed and has as consequence; the like of the other user is removed, i.e you stop liking a user as soon as you are blocked by them.

Dates can only be scheduled if there is a match between two users.
Considering there is a match, dates can be rescheduled if the latest proposal status is 'reschedule'.
If the latest proposal status is not 'reschedule', dates cannot be proposed even if there is a match, as a date was already proposed and determined.

When user1 blocks user2, any date proposal between both user changes its state to ignored.

When a received date is ignored, it is no longer shown in the MANAGE_DATES view of the proposed. The proposer, whose proposal has been ignored by the recipient, will see it as proposed, so ignoring a date respects the privacy of the user ignoring it.


User experience

Users can create an account, that is created in two stages, first entering email nickname and password and then completing their profile with a photo and other relevant information.
The user, ater the sign up action, will be redirected to the log in one, and after it, to the HOMEPAGE view

The HOMEPAGE view displays profiles of other users that align with the logged-in user preferences in the case the "Show all" button is deactivated or all users in the case it is active, considering also they haven't been liked or blocked by the logged-in user.
The users whose profiles are displayed have preferences that align with the logged-in user, so these displayed users are those that match our references and also who can be interested in us, so users  unless we click on the "Show all" button.
The logged-in user will be able to like these other users and move to the OTHERPROFILE views of them.
The logged-in user can move to his MYPROFILE view and to MANAGE_DATES view.

The MYPROFILE view will allow logged-in users to check their likes, blocks and matches, modify their profile information, including their password, add or delete extra photos to their profile.
and move to the manage-dates view
The logged-in user can access to OTHERPROFILE views of users that are shown in his matches, likes or blocks.
The logged-in user can access to the MODIFY view using the settings button, where he will be able to update personal information, the profile photo, which is displayed for preview, and the matching preferences. In this view the actual values for the current user are preserved and shown. From that view the user can access to the view where the password can be changed.
The logged-in user can add and delete extra photos for his profile without leaving the MYPROFILE view.  
The logged-in user can view his posted photos in a full size.
The logged-in user can move to the MANAGE_DATES view and to the HOMEPAGE view.
The logged-in user can log-out.

The OTHERPROFILE view will allow logged-in users to check other users's , showing their profile information and their extra photos, which can also be seen in full size.
The logged-in user will be able to like and block other users.
The logged-in user will be able to see the status of the last proposal with the other user, if existing
The logged-in user can go to the SCHEDULE_DATE view, depending on several conditions (Check logic considerations)
The logged in user can move to the MYPROFILE view, the HOMEPAGE view and the MANAGE_DATES view .
The logged-in user can view the other user posted photos in a full size

The SCHEDULE_DATE will allow logged-in users to propose dates and reschedule dates to their matches. 
The logged-in user will be able to choose a date and a restaurant for the given date, creating a proposal.
The logged-in user can go back to the OTHERPROFILE view of the user he or she is scheduling a date to.
The logged-in user will be redirected to MANAGE_DATES when the form is submitted and the proposal is created.

The MANAGE_DATES view will have two sections, one that shows sent proposals and other that shows received proposals. 
The logged-in user can filter proposal depending on their status at each section.
The logged-in user can answer received proposals while they are on 'proposed' status.
The logged in user can move to the MYPROFILE view and the HOMEPAGE view.

Extra features

Users can upload extra photos to their profile from the MYPROFILE view. Using a boolean that is true only when the photo is the profile photo, we differentiate between profile photo and extra photos.
An AJAX post method,along with an onclick event, are implemented for this. This event shows the corresponding form and, after uploading the extra photo and before actually adding it, it is previsualized.
Users can get a full view of their uploaded extra photos by clickin on them. This is implemented using an onclick event using Javascript. For exiting this full view mode we can click the X button displayed at the corner or pressing 'Esc' key. This functionality is also implemented for other profiles views, so we can full-view their extra photos.

Users can delete their photos by entering into edit mode. When they enter into edit mode, delete buttons for each image are activated. When clicking one of these buttons, after a confirmation question, an AJAX method is called to delete the photo associated to this button.

Users can check their likes and blocks via two dropdown menus. This is implemented using an onclick event. 
Both dropdowns are synchronized so that they are not shown at the same time.
To 'exit' the dropdowns, we must click outside.

In the HOMEPAGE there is a button that can toggle between "Show all" and "Apply my preferences" in case the user wants to see all users instead of only those that satisfy their preferences. This is done via an onclick event that influences the query made to the database. 

These elements as the full view, the form for adding photos, the dropdowns menus and the edit mode buttons are hidden by default in our HTML, and managed by JavaScript functions.

Users can like or block other users from the OTHERPROFILE view. Two different buttons are used for this. 
These buttons have an onclick association to toggleLike and toggleBlock methods, that call AJAX methods to like/unlike/block/unblock users, following our logic considerations.
Using the AJAX response, methods setBlockButtonState and setLikeButtonState are called. These methods change the class of the buttons, which has the following effect:
	- Block button is red when the user is blocked and white otherwise
	- Like button is green when the user is liked and white otherwise
setBlockButtonState and setLikeButtonState are called also at the initial render of the OTHERPROFILE view.
When a user tries to block a user the user likes or tries to like a user the user has blocked, a message appears on screen to tell the user this is not allowed.
This happens because the AJAX method returns an error in its data. When this is the case, a showNotification method is called in javascript, that displays the specific error for a few seconds in the screen
When logged-in users access to the OTHERPROFILE view of a match, if no proposal has been made or the last proposal status is 'reschedule', a Schedule Date button will appear
Similarly to the change of color in Block and Like buttons, we toggle the class of Schedule Date button using toggleScheduleDateButton method. This is called initially to set the initial state when the view is loaded and is also called after a like action in toggleLike.
Instead of changing the color of the button, we change the visibility of the button, as well as adding or removing the hyperlink to the SCHEDULE_DATE view.

Our data model has been built to allow multiple restaurants in the application. 
Apart from the restaurant class, there is an availability with the slots a restaurant has on a specific night. This number varies as proposals are created or modified.
Also, there is a date_in_restaurant class, which gives the restaurant at which each date proposal is or was supposed to take place. 

In the SCHEDULE_DATE view, a calendar is displayed. We use an AJAX methods here so that, after selecting a date, we retrieve the restaurants available for that date,along with the slots.
This is configured so that when selecting a date in the past, even if restaurants are retrieved, no restaurants are displayed, just a message saying it is not possible to schedule a date in the past.
When a correct date is selected, a form is created using Javascript code. This form uses the information returned by the AJAX method. Submiting it means creating a proposal.

MANAGE_DATES view has a dinamyc filtering feature for Proposed and Received dates that allows to filter proposals at each section by status. 
There are two dropdown menus where users can select one status or all.
A click event for each dropdown is created. This forces a call to filterProposals methods, that compares each proposal's status with the selected value at the dropdown.
We do this comparison because each <li> element that represents a proposal has a class name depending on its status.
When the class coincides with the value selected at the dropdown, the .style.display of that proposal is set as 'block'

Use of generative artificial intelligence

During the development of this project, we used ChatGPT 4o to assist with specific tasks, particularly for writing/correcting certain lines of JavaScript code and understanding specific css methods to improve the user interface.
The use of ChatGPT 4o was limited to very specific scenarios. We found that while the tool is helpful for small tasks, it is less effective for managing the complexity and logic of a project of this scale. For this reason, the majority of the project was developed independently, and we ensured we understood all code included in the final submission.
We have carefully reviewed and tested any code suggestions provided by ChatGPT-4 to ensure they meet the project's requirements and work as intended.

List of users already created in the database

User ID: 1, Profile Name: Carolina, Profile Lastname: Durante, Gender: Gender.male, Year:1995 
User ID: 2, Profile Name: Mago, Profile Lastname: Socket, Gender: Gender.non_binary, Year:1995 
User ID: 4, Profile Name: Glory, Profile Lastname: Sixvain, Gender: Gender.male, Year:1987 
User ID: 5, Profile Name: Jude, Profile Lastname: Line, Gender: Gender.non_binary, Year:2000 
User ID: 6, Profile Name: Eladio, Profile Lastname: Carrion, Gender: Gender.other, Year:1997 
User ID: 7, Profile Name: Aitana, Profile Lastname: Ocaña, Gender: Gender.female, Year:1999 
User ID: 9, Profile Name: ETE, Profile Lastname: SECH, Gender: Gender.male, Year:1998 
User ID: 10, Profile Name: Emisario, Profile Lastname: Martínez, Gender: Gender.male, Year:1990 
User ID: 11, Profile Name: David, Profile Lastname: Bisbal, Gender: Gender.male, Year:1982 
User ID: 12, Profile Name: Pedro, Profile Lastname: Sánchez, Gender: Gender.male, Year:1985 
User ID: 13, Profile Name: Lola, Profile Lastname: Lolita, Gender: Gender.female, Year:1970 
User ID: 14, Profile Name: Lola, Profile Lastname: Indigo, Gender: Gender.other, Year:1990 
User ID: 15, Profile Name: Nivki, Profile Lastname: Nicole, Gender: Gender.female, Year:1998 
User ID: 16, Profile Name: Wojnar, Profile Lastname: Oski, Gender: Gender.male, Year:1970 
User ID: 17, Profile Name: Jeff, Profile Lastname: Bezos, Gender: Gender.male, Year:1965 
User ID: 18, Profile Name: Isa, Profile Lastname: Pantoja, Gender: Gender.female, Year:1967 
User ID: 19, Profile Name: Yo, Profile Lastname: Plex, Gender: Gender.other, Year:1999 
User ID: 20, Profile Name: Tran, Profile Lastname: Ca, Gender: Gender.other, Year:1996 
User ID: 21, Profile Name: Barra, Profile Lastname: Ncas, Gender: Gender.other, Year:1995 
User ID: 24, Profile Name: Dor, Profile Lastname: Aemon, Gender: Gender.non_binary, Year:1980 
User ID: 25, Profile Name: Rat, Profile Lastname: Tuille, Gender: Gender.non_binary, Year:1994 
User ID: 26, Profile Name: Rayo , Profile Lastname: McQueen, Gender: Gender.non_binary, Year:1993 

