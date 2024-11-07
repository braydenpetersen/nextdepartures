import React, { useEffect, useState } from "react";

function index() {
    const [message, setMessage] = useState("Loading..."); // default message
    const [people, setPeople] = useState([]); // default people array

    useEffect(() => {
        fetch("http://localhost:8080/api/test")
            .then((response) => response.json())
            .then((data) => {
                setMessage(data.message);
                setPeople(data.people);
                console.log(data.people);
            });
    }, []);

    return (
        <div>
            <h1>{message}</h1>
            <ul>
                {people.map((person, index) => (
                    <li key={index}>{person}</li>
                ))}
            </ul>
        </div>
    );
}

export default index;
