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

    const [departures, setDepartures] = useState<Departure[]>([]); // default departures structure
    useEffect(() => {
        if (!router.isReady) return;

        const fetchDepartures = () => {
            const stopCode = router.query.stopCode || "02799";
            const apiQuery = `${apiUrl}?stopCode=${stopCode}`;

            fetch(apiQuery)
                .then((response) => response.json())
                .then((data) => {
                    setDepartures(data);
                    console.log(data);
                });
        };

        fetchDepartures();
        const interval = setInterval(fetchDepartures, 30000);

        return () => clearInterval(interval);
    }, [router.isReady, router.query.stopCode]);

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
        <div className="mx-2 font-bold tracking-tight">
            <div
                className="flex justify-between items-center py-10"
                style={{ lineHeight: "100%" }}
            >
                <div>
                    <h1 className="text-[40px] tracking-tight h-full">
                        Departures
                        <span className="font-normal"> | Départs</span>
                    </h1>
                </div>
                <div className="text-[var(--light-grey)]">
                    <h1
                        className="text-[40px] tracking-tight h-full"
                        style={{ fontVariantNumeric: "tabular-nums" }}
                    >
                        {ctime}
                    </h1>
                </div>
            </div>
            <div className="flex w-full">
                <table className="flex-1">
                    <thead className="py-[10vh] tracking-tight bg-[var(--dark-grey)]">
                        <tr className="text-left text-[25px] leading-none my-0">
                            <th className="text-left leading-none my-0 py-[20px]">
                                <div>Scheduled</div>
                                <div className="text-[var(--light-grey)] font-normal">
                                    Programmé
                                </div>
                            </th>
                            <th className="text-left leading-none my-0">
                                <div>Route</div>
                                <div className="text-[var(--light-grey)] font-normal">
                                    Ligne
                                </div>
                            </th>
                            <th className="text-left leading-none my-0">
                                <div>Direction</div>
                                <div className="text-[var(--light-grey)] font-normal">
                                    Direction
                                </div>
                            </th>
                            <th className="text-right leading-none my-0">
                                <div>Platform</div>
                                <div className="text-[var(--light-grey)] font-normal">
                                    Quai
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {departures.map((departure, index) => (
                            <tr
                                key={index}
                                className="border-t-[4px] border-dotted border-[var(--light-grey)] border-collapse"
                            >
                                <td className="text-[40px]">
                                    <div className="flex items-center space-x-4 text-[var(--yellow)]">
                                        <span>{departure.time}</span>
                                        {/* {departure.routeNetwork === "GO" && (
                                            <GOTransitLogo className="inline-block text-8xl ml-2 align-middle" />
                                        )} */}
                                    </div>
                                </td>

                                <td className="text-left">
                                    {isGrtIon(departure) ? (
                                        <GrtIonLogo className="text-[60px] inline-block align-middle" />
                                    ) : (
                                        <div
                                            className="text-[30px] text-center font-lining rounded-[10px] flex-shrink-0 justify-center w-fit px-[10px] min-w-[70px]"
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

                                <td className="text-left text-[40px]">
                                    {isGrtIon(departure) && (
                                        <TrainIcon className="inline-block ml-2 align-middle pr-5" />
                                    )}
                                    {departure.headsign}
                                </td>

                                <td className="text-[40px] text-[var(--light-green)] text-right">
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
