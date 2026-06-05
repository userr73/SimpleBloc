// Get references to the input elements
startTime = document.getElementById("start_time");
endTime = document.getElementById("end_time");
allDay = document.getElementById("is_all_day_event");

function pad(value) {
    // Pads the value with a leading zero if it's less than 10
    return String(value).padStart(2, "0");
}

function roundToNearest(event) {
    const element = event.target;

    if (!element.value) return;

    const [hoursStr, minutesStr] = element.value.split(':');
    const minutes = parseInt(minutesStr, 10);
    
    let roundedMinutes = Math.floor(minutes / 5) * 5;
    
    // Gets the remainder of the minutes value
    let remainderMinutes = minutes % 5;
    
    // Round to the correct number of minutes
    if (remainderMinutes >= 3) {
        roundedMinutes += 5;
    }
    
    let time = new Date("1970-01-01T00:00:00"); // Dummy date that does not get affected by daylight savings
    
    // Add the hours and minutes to the date object
    time.setHours(parseInt(hoursStr, 10));
    time.setMinutes(roundedMinutes);
    
    // Convert the time back to a string in the format "HH:MM"
    const localValue = `${pad(time.getHours())}:${pad(time.getMinutes())}`;

    // Update the input value with the rounded time
    element.value = localValue;
}

function updateTime() {
    if (allDay.checked) {
        startTime.value = "";
        startTime.disabled = true;
        endTime.value = "";
        endTime.disabled = true;
    } else {
        startTime.disabled = false;
        endTime.disabled = false;
    }
}

updateTime()

// Add event listeners to the input elements
startTime.addEventListener("blur", roundToNearest);
endTime.addEventListener("blur", roundToNearest);
allDay.addEventListener("change", updateTime);

