import React, { useEffect, useState } from "react";

function index() {
    interface Departure {
        time: string;
        routeNumber: string;
        branch_code: string;
        headsign: string;
        platform: string;
        countdown: string;
        routeColor: string;
        routeTextColor: string;
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
            <div className="flex">
                <h1>Departures</h1>
            </div>
            <div style={{ display: "flex", width: "100%" }}>
                <table style={{ flex: 1 }}>
                    <thead>
                        <tr style={{ backgroundColor: "grey" }}>
                            <th style={{ textAlign: "left" }}>
                                <div>Scheduled</div>
                                <div style={{ fontWeight: 400 }}>Programmé</div>
                            </th>
                            <th style={{ textAlign: "left" }}>
                                <div>Route</div>
                                <div style={{ fontWeight: 400 }}>Ligne</div>
                            </th>
                            <th style={{ textAlign: "left" }}>
                                <div>Destination</div>
                                <div style={{ fontWeight: 400 }}>
                                    Destination
                                </div>
                            </th>
                            <th style={{ textAlign: "right" }}>
                                <div>Platform</div>
                                <div style={{ fontWeight: 400 }}>Quai</div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {departures.map((departure, index) => (
                            <tr key={index}>
                                <td
                                    style={{
                                        textAlign: "left",
                                        color: "yellow",
                                    }}
                                >
                                    {departure.time}
                                </td>

                                <td
                                    style={{
                                        textAlign: "left",
                                        color: `$(departure.routeTextColor)`,
                                        backgroundColor: `$(departure.routeColor)`,
                                    }}
                                >
                                    {departure.routeNumber}
                                    {departure.branch_code}
                                </td>

                                <td style={{ textAlign: "left" }}>
                                    {departure.headsign}
                                </td>

                                <td
                                    style={{
                                        textAlign: "right",
                                        color: "lightgreen",
                                    }}
                                >
                                    {departure.platform}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default index;
