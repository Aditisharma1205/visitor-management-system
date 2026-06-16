import {
    BrowserRouter,
    Routes,
    Route,
} from "react-router-dom";

import Navbar from "./components/Navbar";

import Home from "./pages/Home";

import Register from "./pages/Register";

import Recognize from "./pages/Recognize";

import Users from "./pages/Users";

function App() {
    return (
        <BrowserRouter>
            <Navbar />

            <Routes>
                <Route
                    path="/"
                    element={<Home />}
                />

                <Route
                    path="/register"
                    element={<Register />}
                />

                <Route
                    path="/recognize"
                    element={<Recognize />}
                />

                <Route
                    path="/users"
                    element={<Users />}
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;