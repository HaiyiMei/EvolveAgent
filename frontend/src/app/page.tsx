'use client'

import { useEffect, useRef, useState } from 'react'
import {
  Box,
  Button,
  Container,
  Heading,
  Progress,
  Text,
  Textarea,
  VStack,
  HStack,
  useToast,
  IconButton,
  Table,
  Thead,
  Tbody,
  Tr,
  Td,
  TableContainer,
  Grid,
  GridItem,
  Link,
  Image,
} from '@chakra-ui/react'
import axios from 'axios'
import getConfig from 'next/config'

// Get runtime config
const { publicRuntimeConfig } = getConfig() || { publicRuntimeConfig: {} }

// Use runtime config with fallbacks, checking both runtime config and env variables
const API_URL = publicRuntimeConfig?.API_URL || process.env.API_URL || 'http://localhost:8888/api/v1'
const WS_URL = publicRuntimeConfig?.WS_URL || process.env.WS_URL || 'ws://localhost:8888/api/v1'
const N8N_PUBLIC_URL = publicRuntimeConfig?.N8N_PUBLIC_URL || process.env.N8N_PUBLIC_URL || 'http://localhost:5678'

const GITHUB_REPO = "https://github.com/HaiyiMei/EvolveAgent"

const PREDEFINED_PROMPTS = [
  {
    title: "Chat with OpenAI",
    description: "Setup a workflow of chatting with OpenAI Chat Model",
  },
  {
    title: "Weather Information",
    description: "Setup a workflow of getting weather information for a location",
  },
]

export default function Home() {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const [result, setResult] = useState('')
  const [currentIteration, setCurrentIteration] = useState(0)
  const [maxIterations, setMaxIterations] = useState(5)
  const [workflowUrls, setWorkflowUrls] = useState<Array<{ iteration: number, url: string }>>([])
  const toast = useToast()
  const wsRef = useRef<WebSocket | null>(null)
  const logsEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll logs to bottom
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  // Parse iteration from logs
  useEffect(() => {
    const iterationRegex = /\[Agent\] Iteration (\d+) of (\d+)/
    for (const log of logs) {
      const match = log.match(iterationRegex)
      if (match) {
        setCurrentIteration(parseInt(match[1]))
        setMaxIterations(parseInt(match[2]))
      }
    }
  }, [logs])

  // Parse workflow ID from logs
  useEffect(() => {
    const workflowRegex = /"name":\s*"[^"]+",\s*"id":\s*"([A-Za-z0-9]+)"/
    for (const log of logs) {
      const match = log.match(workflowRegex)
      if (match) {
        const workflowId = match[1]
        const url = `${N8N_PUBLIC_URL}/workflow/${workflowId}`
        setWorkflowUrls(prev => {
          // Check if this URL already exists
          if (!prev.some(item => item.url === url)) {
            return [...prev, { iteration: currentIteration, url }]
          }
          return prev
        })
      }
    }
  }, [logs, currentIteration])

  // Setup WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      // Don't create a new connection if one already exists and is open
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        console.log('WebSocket connection already exists')
        return
      }

      // Close any existing connection before creating a new one
      if (wsRef.current) {
        wsRef.current.close()
      }

      const ws = new WebSocket(`${WS_URL}/agent/logs`)

      ws.onopen = () => {
        console.log('WebSocket Connected')
      }

      ws.onmessage = (event) => {
        setLogs(prev => [...prev, event.data])
      }

      ws.onclose = (event) => {
        console.log('WebSocket Disconnected', event.code, event.reason)
        wsRef.current = null
        // Only try to reconnect if the close wasn't intentional
        if (event.code !== 1000 && event.code !== 1008) {
          setTimeout(connectWebSocket, 5000)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket Error:', error)
      }

      wsRef.current = ws
    }

    connectWebSocket()

    // Cleanup function
    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null // Remove onclose handler to prevent reconnection
        wsRef.current.close(1000, 'Component unmounting')
        wsRef.current = null
      }
    }
  }, []) // Empty dependency array to run only once on mount

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a prompt',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setIsLoading(true)
    setLogs([])
    setResult('')
    setCurrentIteration(0)
    setWorkflowUrls([])

    try {
      const response = await axios.post(`${API_URL}/agent/pipeline`, {
        prompt: prompt.trim(),
        max_iteration: 5,
      })
      setResult(JSON.stringify(response.data, null, 2))
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to generate workflow',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearLogs = () => {
    setLogs([])
    setCurrentIteration(0)
  }

  const handleCopyUrl = (url: string) => {
    navigator.clipboard.writeText(url)
    toast({
      title: 'URL Copied',
      description: 'Workflow URL has been copied to clipboard',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const handlePromptSelect = (description: string) => {
    setPrompt(description)
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Box>
          <HStack justify="space-between" align="center">
            <Box>
              <Heading as="h1" size="xl" mb={2}>
                Workflow Generator
              </Heading>
              <Text fontSize="lg" color="gray.500" mb={4}>
                Generate n8n workflows using natural language prompts
              </Text>
            </Box>
            <Link href={GITHUB_REPO} isExternal>
              <Image
                src="https://img.shields.io/github/stars/HaiyiMei/EvolveAgent?style=social"
                alt="GitHub Repository"
                height="20px"
              />
            </Link>
          </HStack>
        </Box>

        <Grid templateColumns="1fr 1fr" gap={6}>
          {/* Left Column - Input and Controls */}
          <GridItem>
            <Box bg="gray.700" p={4} borderRadius="md">
              <Heading as="h3" size="md" mb={4}>
                Describe your workflow
              </Heading>
              <VStack spacing={4} align="stretch">
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your workflow description here or select a template..."
                  size="lg"
                  rows={4}
                  isDisabled={isLoading}
                />

                <Button
                  colorScheme="blue"
                  size="lg"
                  onClick={handleSubmit}
                  isLoading={isLoading}
                  loadingText="Generating..."
                >
                  Generate Workflow
                </Button>

                {isLoading && (
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" fontWeight="medium">
                        Generation Progress
                      </Text>
                      <Text fontSize="sm" color="gray.500">
                        Iteration {currentIteration} of {maxIterations}
                      </Text>
                    </HStack>
                    <Progress
                      value={(currentIteration / maxIterations) * 100}
                      size="sm"
                      colorScheme="blue"
                      hasStripe
                      isAnimated
                    />
                  </Box>
                )}
              </VStack>
            </Box>
          </GridItem>

          {/* Right Column - Templates */}
          <GridItem>
            <Box bg="gray.700" p={4} borderRadius="md">
              <Heading as="h3" size="md" mb={4}>
                Quick Start Templates
              </Heading>
              <VStack align="stretch" spacing={3}>
                {PREDEFINED_PROMPTS.map((promptItem, index) => (
                  <Box
                    key={index}
                    bg="gray.800"
                    p={4}
                    borderRadius="md"
                    cursor="pointer"
                    _hover={{ bg: 'blue.700' }}
                    onClick={() => handlePromptSelect(promptItem.description)}
                  >
                    <VStack align="stretch" spacing={2}>
                      <HStack justify="space-between">
                        <Text fontWeight="bold" color="blue.300">
                          {promptItem.title}
                        </Text>
                        <Button
                          size="sm"
                          variant="ghost"
                          colorScheme="blue"
                          onClick={(e) => {
                            e.stopPropagation()
                            handlePromptSelect(promptItem.description)
                          }}
                        >
                          Use Template
                        </Button>
                      </HStack>
                      <Text fontSize="sm" color="gray.300">
                        {promptItem.description}
                      </Text>
                    </VStack>
                  </Box>
                ))}
              </VStack>
            </Box>
          </GridItem>
        </Grid>

        {workflowUrls.length > 0 && (
          <Box
            bg="blue.700"
            p={4}
            borderRadius="md"
          >
            <VStack align="stretch" spacing={2}>
              <Heading as="h3" size="md">
                Generated Workflows
              </Heading>
              <VStack align="stretch" spacing={2}>
                {workflowUrls.map((workflow, index) => (
                  <HStack key={index}>
                    <Text color="blue.200" fontSize="sm" minW="100px">
                      Iteration {workflow.iteration}:
                    </Text>
                    <Text color="white" fontSize="sm" flex="1">
                      <a href={workflow.url} target="_blank" rel="noopener noreferrer">
                        {workflow.url} ↗
                      </a>
                    </Text>
                    <Button
                      size="sm"
                      onClick={() => handleCopyUrl(workflow.url)}
                      colorScheme="blue"
                    >
                      Copy
                    </Button>
                  </HStack>
                ))}
              </VStack>
            </VStack>
          </Box>
        )}

        <Box
          bg="gray.700"
          p={4}
          borderRadius="md"
          maxH="300px"
          overflowY="auto"
        >
          <Heading as="h3" size="md" mb={2}>
            Execution Log
          </Heading>
          <VStack align="stretch" spacing={1}>
            {logs.map((log, index) => {
              // Highlight iteration logs
              const isIterationLog = log.includes("[Agent] Iteration")
              return (
                <Text
                  key={index}
                  fontSize="sm"
                  fontFamily="mono"
                  color={isIterationLog ? "blue.300" : undefined}
                  fontWeight={isIterationLog ? "bold" : undefined}
                >
                  {log}
                </Text>
              )
            })}
            <div ref={logsEndRef} />
          </VStack>
          {logs.length === 0 && (
            <Text color="gray.500">No logs yet...</Text>
          )}
        </Box>

        {result && (
          <Box
            bg="gray.700"
            p={4}
            borderRadius="md"
            maxH="400px"
            overflowY="auto"
          >
            <VStack align="stretch" spacing={2}>
              <Heading as="h3" size="md">
                Result
              </Heading>
              <Text as="pre" fontSize="sm" fontFamily="mono" whiteSpace="pre-wrap">
                {result}
              </Text>
            </VStack>
          </Box>
        )}

        <Button
          variant="outline"
          onClick={handleClearLogs}
          isDisabled={logs.length === 0}
        >
          Clear Logs
        </Button>
      </VStack>
    </Container>
  )
}
