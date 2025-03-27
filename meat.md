'''mermaid
flowchart TD
    A[Start: Need to talk to someone] --> B{Are they on travel?}
    B -- Yes --> F[Frustration mounts]
    B -- No --> C{Are they on leave?}
    C -- Yes --> F
    C -- No --> D{Working on another project?}
    D -- Yes --> F
    D -- No --> E{Are they in the lab?}
    E -- Yes --> F
    E -- No --> G{Are they in a meeting?}
    G -- Yes --> F
    G -- No --> H{Is someone already talking to them?}
    H -- Yes --> F
    H -- No --> I{Are they busy?}
    I -- Yes --> F
    I -- No --> J{Are they the only person you need to talk to?}
    J -- Yes --> K[Proceed with conversation]
    J -- No --> L[How many people?]
    L --> M[Repeat process for each person]
    M --> F[Frustration escalates]
'''

'''
function attemptToTalk(person):
    if person.isOnTravel():
        triggerFrustration("Person is traveling")
    else if person.isOnLeave():
        triggerFrustration("Person is on leave")
    else if person.isWorkingOnAnotherProject():
        triggerFrustration("Person is busy on another project")
    else if person.isInLab():
        triggerFrustration("Person is in the lab")
    else if person.isInMeeting():
        triggerFrustration("Person is in a meeting")
    else if person.isAlreadyBeingTalkedTo():
        triggerFrustration("Someone else is already talking to the person")
    else if person.isBusy():
        triggerFrustration("Person is busy")
    else:
        // Person is available
        talkTo(person)

function main():
    peopleList = getPeopleToTalkTo()  // List of people you need to speak with
    
    if length(peopleList) == 1:
        attemptToTalk(peopleList[0])
    else:
        for person in peopleList:
            attemptToTalk(person)
            // Redo the process for each additional person, increasing frustration
            triggerFrustration("Need to repeat the process for another person")
'''

