import { createBrowserRouter } from "react-router-dom";
import App from "./App";
import Login from "./components/login";
// import Lend from "./components/lend";
import SignUp from "./components/signUp";
import AddBook from "./components/addBook";
//import AddComment from "./components/addComment";
import UserProvider from "./context/userContext";
import Admin from "./components/admin";
import Home from "./components/home";
import Header from "./components/header";
import Lends from "./components/lend";
import Show from "./components/allBook";
const Routers = createBrowserRouter([
    {
        path: "",
     element: <UserProvider><App/></UserProvider>,

        children: [
            {
            path:"",
            element:<Home/>
            },
            {
            path: "Show/",
            element: <Show/>,
            },
            {
                path:"header",
                element:<Header/>
            },
            {
            path: "Login/",
            element: <Login />
            },
            {
            path: "SignUp",
            element: <SignUp />
            },
            {
            path: "Lends",
            element: <Lends />
        },
            {
            path:"Home",
            element:<Home/>
            },
            
            {
            path:"admin",
            element:<Admin/>,
            children:[
                {
                    path:"addBook",
                    element:<AddBook/>
                }
            ]
            },
            // {
            // path:"AddComment",
            //     element:<AddComment/>
            // },
            
            
        
        ]}])
    






export default Routers;