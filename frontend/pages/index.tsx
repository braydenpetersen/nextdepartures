import React, { useEffect, useState } from "react";

function index() {
    interface Departure {
        departureTime: string;
        routeNumber: string;
        branch_code: string;
        headsign: string;
        platform: string;
        countdown: string;
    }

    const [departures, setDepartures] = useState<Departure[]>([]); // default departures structure

    useEffect(() => {
        fetch("http://localhost:8080/api/departures")
            .then((response) => response.json())
            .then((data) => {
                setDepartures(data);
                console.log(data);
            });
    }, []);

    return (
        <div>
            <h1 >Departures</h1>
            <ul>
                {departures.map((departure, index) => (
                    <li key={index}>
                        {departure.departureTime} {departure.countdown}min [{departure.routeNumber}{departure.branch_code}] to {departure.headsign} --- Platform {departure.platform}
                    </li>
                ))}
            </ul>
        </div>
    );

}

export default index;
