import { GrtIonLogo, TrainIcon, GOTransitLogo } from "../components/svg";
import React, { useEffect, useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

function Index() {
    interface Departure {
        time: string;
        routeNumber: string;
        branchCode: string;
        headsign: string;
        platform: string;
        countdown: string;
        routeColor: string;
        routeTextColor: string;
        routeNetwork: string;
    }

    const [departures, setDepartures] = useState<Departure[]>([]); // default departures structure
    useEffect(() => {
        const fetchDepartures = () => {
            fetch(`${apiUrl}`)
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

    const isGrtIon = (departure: Departure) => {
        return (
            departure.routeNetwork === "GRT" && departure.routeNumber === "301"
        );
    };

    return (
        <div>
            <div className="title">
                <div>
                    <h1>
                        Departures <span className="title-fr">| Départs</span>
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
                                <td className="time">
                                    <div className="flex items-center space-x-4">
                                        <span>{departure.time}</span>
                                        {/* {departure.routeNetwork === "GO" && (
                                            <GOTransitLogo className="inline-block text-8xl ml-2 align-middle" />
                                        )} */}
                                        {isGrtIon(departure) && (
                                            <TrainIcon className="inline-block ml-2 align-middle" />
                                        )}
                                    </div>
                                </td>

                                <td
                                    style={{
                                        textAlign: "left",
                                    }}
                                >
                                    {isGrtIon(departure) ? (
                                        <GrtIonLogo className="text-8xl" />
                                    ) : (
                                        <div
                                            className="route"
                                            style={{
                                                color: departure.routeTextColor,
                                                backgroundColor:
                                                    departure.routeColor,
                                            }}
                                        >
                                            {departure.routeNumber}
                                            {departure.branchCode}
                                        </div>
                                    )}
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
