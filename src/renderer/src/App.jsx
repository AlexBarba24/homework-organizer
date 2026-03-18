import { useState } from 'react'
// import { useForm } from 'react-hook-form'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.css'
// import './assets/base.css'
import './assets/main.css'
import FileSubmissionBox from './components/FileSubmissionBox'
import AssignmentConfirmation from './components/AssignmentConfirmation'

const scene = {
  CHOOSE_SCHOOL: 1,
  LOGIN: 2,
  DASHBOARD: 3
}

// const SchoolToUsername = {
//   Michigan: 'uniqname',
//   'Boston College': 'username',
//   WPI: 'username'
// }

function App() {
  // const ipcHandle = () => window.electron.ipcRenderer.send('ping')
  // const [school, setSchool] = useState('Undecided')
  const [currentScene, setCurrentScene] = useState(scene.CHOOSE_SCHOOL)
  const [assignments, setAssignments] = useState([])
  const [showConfirmation, setShowConfirmation] = useState(false)
  // const [invalidPass, setInvalidPass] = useState(false)
  // const schools = ['Michigan', 'Boston College', 'WPI']
  // const { register, getValues } = useForm()

  // const fetchSchool = async () => {
  //   const res = await axios.get('http://127.0.0.1:8080/api/get_school')
  //   console.log(res.data.school)
  //   setSchool(res.data.school)
  // }

  // const postSchool = async (name) => {
  //   await axios.post('http://127.0.0.1:8080/api/set_school', { name: name })
  //   await fetchSchool()
  // }

  const handleParseComplete = (parsedAssignments) => {
    if (parsedAssignments && parsedAssignments.length > 0) {
      setAssignments(parsedAssignments)
      setShowConfirmation(true)
    } else {
      alert('No assignments found in the PDF. Please try a different file.')
    }
  }

  const handleConfirmationCancel = () => {
    setShowConfirmation(false)
    setAssignments([])
  }

  const handleConfirmationComplete = () => {
    setShowConfirmation(false)
    setAssignments([])
    // Optionally show a success message or navigate to a different scene
  }

  // const login = async (username, password) => {
  //   let response = await axios.post('http://127.0.0.1:8080/api/login', {
  //     user: username,
  //     pass: password
  //   })
  //   if (!response.data.success) {
  //     setInvalidPass(true)
  //     return
  //   }
  //   setCurrentScene(scene.DASHBOARD)
  //   setInvalidPass(false)
  // }

  return (
    <>
      {currentScene === scene.CHOOSE_SCHOOL && !showConfirmation && (
        <>
          <div className="creator">Organize your assignments!</div>
          <div className="text react">Upload your PDF</div>
          {/*<p className="tip">Current School is: {school}</p>*/}
          {/*<div className="actions">*/}
          {/*  {schools.map((value) => (*/}
          {/*    <div key={value} className={'action' + (value === school ? ' sel-btn-hvr' : '')}>*/}
          {/*      <a target="_blank" rel="noreferrer" onClick={async () => postSchool(value)}>*/}
          {/*        {value}*/}
          {/*      </a>*/}
          {/*    </div>*/}
          {/*  ))}*/}
          {/*</div>*/}
          <FileSubmissionBox onParseComplete={handleParseComplete} />
        </>
      )}
      {showConfirmation && (
        <>
          <div className="creator">Organize your assignments!</div>
          <AssignmentConfirmation
            assignments={assignments}
            onCancel={handleConfirmationCancel}
            onComplete={handleConfirmationComplete}
          />
        </>
      )}
    </>
    //     {currentScene === scene.CHOOSE_SCHOOL && (
    //       <>
    //         <img alt="logo" className="logo" src={electronLogo} />
    //         <div className="creator">Organize your assignments!</div>
    //         <div className="text react">Select a School Below</div>
    //         <p className="tip">Current School is: {school}</p>
    //         <div className="actions">
    //           {schools.map((value) => (
    //             <div key={value} className={'action' + (value === school ? ' sel-btn-hvr' : '')}>
    //               <a target="_blank" rel="noreferrer" onClick={async () => postSchool(value)}>
    //                 {value}
    //               </a>
    //             </div>
    //           ))}
    //         </div>
    //         <img
    //           alt="continue"
    //           className="arrow"
    //           src={rightArrow}
    //           onClick={() => setCurrentScene(scene.LOGIN)}
    //         />
    //       </>
    //     )}
    //     {currentScene === scene.LOGIN && (
    //       <>
    //         {invalidPass && <h3>Invalid Username or Password</h3>}
    //         <form>
    //           <div className="form-floating mb-3">
    //             <input
    //               {...register('username')}
    //               type="username"
    //               className="form-control"
    //               name="username"
    //               id="floatingInput"
    //               placeholder="name@example.com"
    //             />
    //             <label htmlFor="floatingInput">{SchoolToUsername[school]}</label>
    //           </div>
    //           <div className="form-floating">
    //             <input
    //               {...register('password')}
    //               type="password"
    //               name="password"
    //               className="form-control"
    //               id="floatingPassword"
    //               placeholder="Password"
    //             />
    //             <label htmlFor="floatingPassword">Password</label>
    //           </div>
    //           <div className="actions">
    //             <div className="action always-hvr">
    //               <a
    //                 onClick={() => {
    //                   const values = getValues()
    //                   return login(values['username'], values['password'])
    //                 }}
    //               >
    //                 Login
    //               </a>
    //             </div>
    //           </div>
    //         </form>
    //       </>
    //     )}
    //   </>
  )
}

export default App
