import React, { useEffect, useState } from "react";

function Index() {
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
        const fetchDepartures = () => {
            fetch("http://localhost:8080/api/departures")
                .then((response) => response.json())
                .then((data) => {
                    setDepartures(data);
                    console.log(data);
                });
        };

        fetchDepartures();
        const interval = setInterval(fetchDepartures, 30000);
        return () => clearInterval(interval);
    }, []);

    const [ctime, setCtime] = useState("");

    useEffect(() => {
        setCtime(
            new Date().toLocaleTimeString("en-GB", {
                timeZone: "America/Toronto",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            })
        );

        const timer = setInterval(() => {
            setCtime(
                new Date().toLocaleTimeString("en-GB", {
                    timeZone: "America/Toronto",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                })
            );
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    return (
        <div>
            <div className="title">
                <div>
                    <h1>
                        Departures{" "}
                        <span className="title-fr">| Départs</span>
                    </h1>
                </div>
                <div className="clock">
                    <h1 style={{ fontVariantNumeric: "tabular-nums" }}>
                        {ctime}
                    </h1>
                </div>
            </div>
            <div style={{ display: "flex", width: "100%" }}>
                <table style={{ flex: 1 }}>
                    <thead>
                        <tr>
                            <th style={{ textAlign: "left" }}>
                                <div>Scheduled</div>
                                <div className="header-fr">Programmé</div>
                            </th>
                            <th style={{ textAlign: "left" }}>
                                <div>Route</div>
                                <div className="header-fr">Ligne</div>
                            </th>
                            <th style={{ textAlign: "left" }}>
                                <div>Direction</div>
                                <div className="header-fr">Direction</div>
                            </th>
                            <th style={{ textAlign: "right" }}>
                                <div>Platform</div>
                                <div className="header-fr">Quai</div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {departures.map((departure, index) => (
                            <tr key={index}>
                                <td className="time">{departure.time}</td>

                                <td
                                    style={{
                                        textAlign: "left",
                                    }}
                                >
                                    <div
                                        className="route"
                                        style={{
                                            color: departure.routeTextColor,
                                            backgroundColor:
                                                departure.routeColor,
                                        }}
                                    >
                                        {departure.routeNumber}
                                        {departure.branch_code}
                                    </div>
                                </td>

                                <td style={{ textAlign: "left" }}>
                                    {departure.headsign}
                                </td>

                                <td className="platform">
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

export default Index;
