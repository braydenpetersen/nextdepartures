import React, { useEffect, useState } from "react";

function index() {
    const [departures, setDepartures] = useState({
        time: "XX:XX",
        routeNumber: "",
        routeColor: "",
        routeTextColor: "",
        headsign: "",
        global_stop_id: "",
        stop_code: "",
        branch_code: "",
    }); // default departures structure

    useEffect(() => {
        fetch("http://localhost:8080/api/departures")
            .then((res) => res.json())
            .then((departures) => {
                setDepartures({
                    time: departures.time,
                    routeNumber: departures.routeNumber,
                    routeColor: departures.routeColor,
                    routeTextColor: departures.routeTextColor,
                    headsign: departures.headsign,
                    global_stop_id: departures.global_stop_id,
                    stop_code: departures.stop_code,
                    branch_code: departures.branch_code,
                });
            });
    }, []);

    return (
        <div>
            <h1>Departures</h1>
            <p>{departures.time}</p>
        </div>
    );
}

export default index;
