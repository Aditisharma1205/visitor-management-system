import {
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Register from "./pages/Register";
import Users from "./pages/Users";
import Search from "./pages/Search";
import AdminMonitor from "./pages/AdminMonitor";
import SessionHistory from "./pages/SessionHistory";

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
                path="/monitor"
                element={
                    <Layout>
                        <AdminMonitor />
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

            <Route
                path="/search"
                element={
                    <Layout>
                        <Search />
                    </Layout>
                }
            />

            <Route
                path="/history"
                element={
                    <Layout>
                        <SessionHistory />
                    </Layout>
                }
            />

            {/* Catch-all: unknown paths (e.g. old /recognize bookmarks) redirect home instead of rendering blank */}
            <Route
                path="*"
                element={
                    <Navigate
                        to="/dashboard"
                        replace
                    />
                }
            />

        </Routes>
    );
}

export default App;