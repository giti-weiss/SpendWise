import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import './App.css'
// import Show from './components/allBook'
import Header from './components/header'
import Login from './components/login'

function App() {
  <link
  rel="stylesheet"
  href="https://fonts.googleapis.com/icon?family=Material+Icons"
/>
  const [count, setCount] = useState(0)
  return (
    <>
    <Header/>
    <Outlet/>
      {/* <div>כותרת</div>
      <header/>
      <div>תוכן
        <p>הרשמה</p>
        <p>כניסה</p>
        <p>הצגת כל הספרים</p>
        <Show/>
        <p>מסך השאלת ספרים שלי</p>
      </div>
      <div>סיום</div> */}
    </>
  )
}

export default App
