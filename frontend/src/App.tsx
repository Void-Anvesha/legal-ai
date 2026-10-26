import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Chat from './pages/Chat'
import Summary from './pages/Summary'
import Cases from './pages/Cases'
import Intake from './pages/Intake'
import Review from './pages/Review'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="w-full px-4 py-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/intake" element={<Intake />} />
          <Route path="/review" element={<Review />} />
          <Route path="/review/:caseId" element={<Review />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:documentId" element={<Chat />} />
          <Route path="/summary/:documentId" element={<Summary />} />
          <Route path="/cases" element={<Cases />} />
          <Route path="/cases/:documentId" element={<Cases />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
