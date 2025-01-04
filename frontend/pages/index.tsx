import { GrtIonLogo, TrainIcon } from "../components/svg";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";


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

    const router = useRouter();
    const { stopCode } = router.query;
    let apiQuery = "";

    const [departures, setDepartures] = useState<Departure[]>([]); // default departures structure
    useEffect(() => {
        const fetchDepartures = () => {
            if (stopCode) {
                apiQuery = `${apiUrl}?stopCode=${stopCode}`;
            } else {
                apiQuery = `${apiUrl}?stopCode=02799`;
            }

            fetch(`${apiQuery}`)
                .then((response) => response.json())
                .then((data) => {
                    setDepartures(data);
                    console.log(data);
                });
        };

        fetchDepartures();
        const interval = setInterval(fetchDepartures, 30000);
        return () => clearInterval(interval);
    }, [stopCode]);

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
            <div className="flex justify-between items-center py-12" style={{ lineHeight: "100%" }}>
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
            <div className="flex w-full">
                <table className="flex-1">
                    <thead>
                        <tr>
                            <th className="text-left">
                                <div>Scheduled</div>
                                <div className="header-fr">Programmé</div>
                            </th>
                            <th className="text-left">
                                <div>Route</div>
                                <div className="header-fr">Ligne</div>
                            </th>
                            <th className="text-left">
                                <div>Direction</div>
                                <div className="header-fr">Direction</div>
                            </th>
                            <th className="text-right">
                                <div>Platform</div>
                                <div className="header-fr">Quai</div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {departures.map((departure, index) => (
                            <tr key={index} className="border-collapse">
                                <td className="time" >
                                    <div className="flex items-center space-x-4 text-[var(--yellow)]">
                                        <span>{departure.time}</span>
                                        {/* {departure.routeNetwork === "GO" && (
                                            <GOTransitLogo className="inline-block text-8xl ml-2 align-middle" />
                                        )} */}
                                    </div>
                                </td>

                                <td className="text-left">
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

                                <td className="text-left">
                                    {isGrtIon(departure) && (
                                        <TrainIcon className="inline-block ml-2 align-middle pr-5"/>
                                    )}
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
