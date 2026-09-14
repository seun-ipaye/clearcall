import { Route, BrowserRouter, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import ByClient from './pages/ByClient'
import ByProvince from './pages/ByProvince'
import ByReason from './pages/ByReason'
import Overview from './pages/Overview'
import TranscriptInsights from './pages/TranscriptInsights'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="by-reason" element={<ByReason />} />
          <Route path="by-client" element={<ByClient />} />
          <Route path="by-province" element={<ByProvince />} />
          <Route path="transcript-insights" element={<TranscriptInsights />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
