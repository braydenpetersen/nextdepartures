import React, { useEffect, useState } from "react";

function index() {
    // const [message, setMessage] = useState("Loading..."); // default message
    // const [people, setPeople] = useState([]); // default people array
    const [departures, setDepartures] = useState([]); // default departures array

    useEffect(() => {
        fetch("http://localhost:8080/api/departures")
            .then((response) => response.json())
            .then((data) => {
                setDepartures(data.departures);
            });
    }, []);

    return (
        <div>
            <h1>Departures</h1>
            <pre>{JSON.stringify(departures, null, 2)}</pre>
        </div>
    );
}

export default index;
