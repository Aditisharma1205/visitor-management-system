import {
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Register from "./pages/Register";
import Recognize from "./pages/Recognize";
import Users from "./pages/Users";

import Layout from "./components/Layout";

function App() {
    return (
        <Routes>

            <Route
                path="/"
                element={
                    <Navigate
                        to="/dashboard"
                        replace
                    />
                }
            />

            <Route
                path="/dashboard"
                element={
                    <Layout>
                        <Dashboard />
                    </Layout>
                }
            />

            <Route
                path="/register"
                element={
                    <Layout>
                        <Register />
                    </Layout>
                }
            />

            <Route
                path="/recognize"
                element={
                    <Layout>
                        <Recognize />
                    </Layout>
                }
            />

            <Route
                path="/users"
                element={
                    <Layout>
                        <Users />
                    </Layout>
                }
            />

        </Routes>
    );
}

export default App;