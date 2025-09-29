import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Home, 
  Car, 
  Smartphone, 
  Lightbulb, 
  Thermometer, 
  Lock, 
  Camera, 
  Mic, 
  MicOff,
  Power,
  Settings,
  Activity,
  MessageCircle,
  Send,
  Volume2,
  Wifi,
  WifiOff,
  Battery,
  Fuel,
  Navigation,
  Shield,
  AlertTriangle
} from 'lucide-react'
import './App.css'

function App() {
  const [isListening, setIsListening] = useState(false)
  const [voiceInput, setVoiceInput] = useState('')
  const [chatMessages, setChatMessages] = useState([
    { id: 1, type: 'ai', message: 'Hello! I\'m your AI assistant. How can I help you today?' }
  ])
  const [devices, setDevices] = useState({
    smartphone: { status: 'connected', battery: 85, location: 'Home' },
    car: { status: 'connected', fuel: 75, location: 'Garage', engine: false },
    home: {
      lights: { living_room: true, bedroom: false, kitchen: true },
      thermostat: { temperature: 72, mode: 'auto' },
      locks: { front_door: true, back_door: true },
      security: { armed: false, cameras: 4 }
    }
  })

  const [systemStats] = useState({
    totalDevices: 12,
    activeDevices: 10,
    offlineDevices: 2,
    tasksCompleted: 47,
    energySaved: '23%'
  })

  const handleVoiceToggle = () => {
    setIsListening(!isListening)
    if (!isListening) {
      // Simulate voice recognition
      setTimeout(() => {
        setVoiceInput('Turn on the living room lights')
        setIsListening(false)
      }, 2000)
    }
  }

  const handleSendMessage = () => {
    if (voiceInput.trim()) {
      const newMessage = { 
        id: chatMessages.length + 1, 
        type: 'user', 
        message: voiceInput 
      }
      setChatMessages([...chatMessages, newMessage])
      
      // Simulate AI response
      setTimeout(() => {
        const aiResponse = { 
          id: chatMessages.length + 2, 
          type: 'ai', 
          message: 'I\'ve turned on the living room lights for you. Is there anything else you need?' 
        }
        setChatMessages(prev => [...prev, aiResponse])
      }, 1000)
      
      setVoiceInput('')
    }
  }

  const toggleDevice = (category, device) => {
    setDevices(prev => ({
      ...prev,
      home: {
        ...prev.home,
        [category]: {
          ...prev.home[category],
          [device]: !prev.home[category][device]
        }
      }
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  JARVIS AI Hub
                </h1>
                <p className="text-sm text-gray-400">Intelligent Home & Life Assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="border-green-500 text-green-400">
                <Wifi className="w-3 h-3 mr-1" />
                Connected
              </Badge>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Dashboard */}
          <div className="lg:col-span-2 space-y-8">
            {/* System Overview */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-blue-400">{systemStats.totalDevices}</div>
                  <div className="text-xs text-gray-400">Total Devices</div>
                </CardContent>
              </Card>
              <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-green-400">{systemStats.activeDevices}</div>
                  <div className="text-xs text-gray-400">Active</div>
                </CardContent>
              </Card>
              <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-red-400">{systemStats.offlineDevices}</div>
                  <div className="text-xs text-gray-400">Offline</div>
                </CardContent>
              </Card>
              <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-purple-400">{systemStats.tasksCompleted}</div>
                  <div className="text-xs text-gray-400">Tasks Today</div>
                </CardContent>
              </Card>
              <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-400">{systemStats.energySaved}</div>
                  <div className="text-xs text-gray-400">Energy Saved</div>
                </CardContent>
              </Card>
            </div>

            {/* Device Control Tabs */}
            <Tabs defaultValue="home" className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-black/40 border-white/10">
                <TabsTrigger value="home" className="data-[state=active]:bg-blue-600">
                  <Home className="w-4 h-4 mr-2" />
                  Home
                </TabsTrigger>
                <TabsTrigger value="car" className="data-[state=active]:bg-blue-600">
                  <Car className="w-4 h-4 mr-2" />
                  Car
                </TabsTrigger>
                <TabsTrigger value="phone" className="data-[state=active]:bg-blue-600">
                  <Smartphone className="w-4 h-4 mr-2" />
                  Phone
                </TabsTrigger>
              </TabsList>

              {/* Home Tab */}
              <TabsContent value="home" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Lighting Control */}
                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Lightbulb className="w-5 h-5 mr-2 text-yellow-400" />
                        Lighting
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {Object.entries(devices.home.lights).map(([room, isOn]) => (
                        <div key={room} className="flex items-center justify-between">
                          <span className="capitalize">{room.replace('_', ' ')}</span>
                          <Button
                            size="sm"
                            variant={isOn ? "default" : "outline"}
                            onClick={() => toggleDevice('lights', room)}
                            className={isOn ? "bg-yellow-500 hover:bg-yellow-600" : ""}
                          >
                            <Power className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  {/* Climate Control */}
                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Thermometer className="w-5 h-5 mr-2 text-blue-400" />
                        Climate
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center">
                        <div className="text-3xl font-bold text-blue-400">
                          {devices.home.thermostat.temperature}°F
                        </div>
                        <div className="text-sm text-gray-400 capitalize">
                          {devices.home.thermostat.mode} mode
                        </div>
                        <div className="flex justify-center space-x-2 mt-4">
                          <Button size="sm" variant="outline">-</Button>
                          <Button size="sm" variant="outline">+</Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Security */}
                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Shield className="w-5 h-5 mr-2 text-green-400" />
                        Security
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span>System Status</span>
                        <Badge variant={devices.home.security.armed ? "destructive" : "secondary"}>
                          {devices.home.security.armed ? "Armed" : "Disarmed"}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Cameras Active</span>
                        <span className="text-green-400">{devices.home.security.cameras}/4</span>
                      </div>
                      {Object.entries(devices.home.locks).map(([door, isLocked]) => (
                        <div key={door} className="flex items-center justify-between">
                          <span className="capitalize">{door.replace('_', ' ')}</span>
                          <Lock className={`w-4 h-4 ${isLocked ? 'text-green-400' : 'text-red-400'}`} />
                        </div>
                      ))}
                    </CardContent>
                  </Card>

                  {/* Quick Actions */}
                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Button className="w-full justify-start" variant="outline">
                        <Home className="w-4 h-4 mr-2" />
                        Good Morning Scene
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Volume2 className="w-4 h-4 mr-2" />
                        Movie Time Scene
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Shield className="w-4 h-4 mr-2" />
                        Good Night Scene
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Car Tab */}
              <TabsContent value="car" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Car className="w-5 h-5 mr-2 text-blue-400" />
                        Vehicle Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span>Connection</span>
                        <Badge variant="outline" className="border-green-500 text-green-400">
                          <Wifi className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Fuel Level</span>
                        <div className="flex items-center">
                          <Fuel className="w-4 h-4 mr-1 text-yellow-400" />
                          <span>{devices.car.fuel}%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Engine</span>
                        <Badge variant={devices.car.engine ? "default" : "secondary"}>
                          {devices.car.engine ? "Running" : "Off"}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Location</span>
                        <span className="text-gray-400">{devices.car.location}</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Remote Controls</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Button className="w-full justify-start" variant="outline">
                        <Power className="w-4 h-4 mr-2" />
                        Start Engine
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Lock className="w-4 h-4 mr-2" />
                        Lock Doors
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Navigation className="w-4 h-4 mr-2" />
                        Find My Car
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Thermometer className="w-4 h-4 mr-2" />
                        Climate Control
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Phone Tab */}
              <TabsContent value="phone" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Smartphone className="w-5 h-5 mr-2 text-green-400" />
                        Device Status
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span>Connection</span>
                        <Badge variant="outline" className="border-green-500 text-green-400">
                          <Wifi className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Battery</span>
                        <div className="flex items-center">
                          <Battery className="w-4 h-4 mr-1 text-green-400" />
                          <span>{devices.smartphone.battery}%</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Location</span>
                        <span className="text-gray-400">{devices.smartphone.location}</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Smart Features</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Button className="w-full justify-start" variant="outline">
                        <Camera className="w-4 h-4 mr-2" />
                        Security Camera
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Mic className="w-4 h-4 mr-2" />
                        Voice Commands
                      </Button>
                      <Button className="w-full justify-start" variant="outline">
                        <Navigation className="w-4 h-4 mr-2" />
                        Location Sharing
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* AI Chat Interface */}
          <div className="space-y-6">
            <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageCircle className="w-5 h-5 mr-2 text-purple-400" />
                  AI Assistant
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Voice and text commands
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Chat Messages */}
                <div className="h-64 overflow-y-auto space-y-3 p-2 bg-black/20 rounded-lg">
                  {chatMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] p-3 rounded-lg text-sm ${
                          msg.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-100'
                        }`}
                      >
                        {msg.message}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Voice Input */}
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Input
                      placeholder="Type a command or use voice..."
                      value={voiceInput}
                      onChange={(e) => setVoiceInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="bg-black/20 border-white/10 text-white placeholder-gray-400"
                    />
                    <Button onClick={handleSendMessage} size="sm">
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <Button
                    onClick={handleVoiceToggle}
                    className={`w-full ${
                      isListening 
                        ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                        : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  >
                    {isListening ? (
                      <>
                        <MicOff className="w-4 h-4 mr-2" />
                        Listening...
                      </>
                    ) : (
                      <>
                        <Mic className="w-4 h-4 mr-2" />
                        Voice Command
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* System Alerts */}
            <Card className="bg-black/40 border-white/10 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-yellow-400" />
                  System Alerts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start space-x-3 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                  <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5" />
                  <div className="text-sm">
                    <div className="font-medium">Low Fuel Alert</div>
                    <div className="text-gray-400">Your car fuel is at 75%</div>
                  </div>
                </div>
                <div className="flex items-start space-x-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <Activity className="w-4 h-4 text-blue-400 mt-0.5" />
                  <div className="text-sm">
                    <div className="font-medium">Energy Optimization</div>
                    <div className="text-gray-400">Saved 23% energy today</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

