"use client";

import React, { useEffect, useState, useMemo } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  type AgentState,
  type ReceivedChatMessage,
  useRoomContext,
  useVoiceAssistant,
  useLocalParticipant,
} from "@livekit/components-react";
import { Track } from "livekit-client";
import { toastAlert } from "@/components/alert-toast";

import { ChatEntry } from "@/components/livekit/chat/chat-entry";
import { ChatMessageView } from "@/components/livekit/chat/chat-message-view";
import { VideoTile } from "@/components/livekit/video-tile";
import { AgentControlBar } from "@/components/livekit/agent-control-bar/agent-control-bar";
import { FaceDetectionPanel } from "@/components/face-detection/face-detection-panel";
import { FaceDetectionToggle } from "@/components/face-detection/face-detection-toggle";
import useChatAndTranscription from "@/hooks/useChatAndTranscription";
import { useDebugMode } from "@/hooks/useDebug";
import type { AppConfig } from "@/lib/types";
import { cn } from "@/lib/utils";
import { safeDisconnect } from "@/lib/room-utils";
import { useRouter } from "next/navigation";

function isAgentAvailable(agentState: AgentState) {
  return (
    agentState == "listening" ||
    agentState == "thinking" ||
    agentState == "speaking"
  );
}

// Helper function to get local track reference
function useLocalTrackRef(source: Track.Source) {
  const { localParticipant } = useLocalParticipant();
  const publication = localParticipant.getTrackPublication(source);
  const trackRef = useMemo(
    () =>
      publication
        ? { source, participant: localParticipant, publication }
        : undefined,
    [source, publication, localParticipant],
  );
  return trackRef;
}

interface SessionViewProps {
  appConfig: AppConfig;
  disabled: boolean;
  sessionStarted: boolean;
  onEndCallStarted?: () => void;
}

export const SessionView = ({
  appConfig,
  disabled,
  sessionStarted,
  onEndCallStarted,
  ref,
}: React.ComponentProps<"div"> & SessionViewProps) => {
  const { state: agentState } = useVoiceAssistant();
  const [chatOpen, setChatOpen] = useState(false);
  const [faceDetectionActive, setFaceDetectionActive] = useState(false);
  const [faceAnalysisData, setFaceAnalysisData] = useState<any>({});
  const { messages, send } = useChatAndTranscription();
  const room = useRoomContext();
  const router = useRouter();

  // Add ref to prevent infinite cycling
  const hasStartedFaceDetection = React.useRef(false);
  const hasEndedInterview = React.useRef(false);
  const faceDetectionRef = React.useRef<{ forceDisconnect: () => void }>(null);

  // Start face detection automatically when session starts
  useEffect(() => {
    console.log("🔍 Face detection check:", {
      sessionStarted,
      messagesLength: messages.length,
      faceDetectionActive,
    });

    if (
      sessionStarted &&
      !faceDetectionActive &&
      !hasStartedFaceDetection.current &&
      !hasEndedInterview.current
    ) {
      console.log("🎯 Starting face detection - session has started");
      setFaceDetectionActive(true);
      hasStartedFaceDetection.current = true;
    }
  }, [sessionStarted, faceDetectionActive]);

  // Stop face detection when interview ends (when AI says goodbye)
  useEffect(() => {
    const latestAgentMessage = messages
      .filter((msg) => !msg.from?.isLocal)
      .pop();
    if (latestAgentMessage && !hasEndedInterview.current) {
      const normalizedMsg =
        latestAgentMessage.message
          ?.toLowerCase()
          .replace(/[^a-z0-9 ]/gi, "")
          .trim() || "";
      const endRegex = /(have a great day|thank)/i;
      if (endRegex.test(normalizedMsg) && faceDetectionActive) {
        console.log(
          "🛑 Interview ended - but keeping face detection active until user ends call",
        );
        hasEndedInterview.current = true; // Mark that interview has ended
        // Don't stop face detection here - let user end it manually
      }
    }
  }, [messages, faceDetectionActive]);

  // Cleanup face detection when component unmounts
  useEffect(() => {
    return () => {
      if (faceDetectionActive) {
        console.log("🛑 Cleaning up face detection on unmount");
        setFaceDetectionActive(false);
        hasStartedFaceDetection.current = false;
        hasEndedInterview.current = false;
      }
    };
  }, []); // Remove faceDetectionActive from dependencies

  // Debug router navigation
  useEffect(() => {
    console.log("📍 Current pathname:", window.location.pathname);
  }, []);

  const handleRouterPush = (path: string) => {
    console.log(`🚀 Router.push called with path: ${path}`);
    // Use window.location.href for hard navigation to prevent refresh issues
    window.location.href = path;
  };

  const [hasNavigated, setHasNavigated] = useState(false);

  // Get camera track
  const cameraTrack = useLocalTrackRef(Track.Source.Camera);
  const isCameraEnabled = cameraTrack && !cameraTrack.publication.isMuted;

  // Typing effect states
  const [isTyping, setIsTyping] = useState(false);
  const [typingText, setTypingText] = useState("");
  const [currentMessage, setCurrentMessage] = useState<any>(null);
  const [typingSpeed] = useState(50); // milliseconds per character

  // Chat clearing states
  const [shouldClearChat, setShouldClearChat] = useState(false);
  const [lastMessageCount, setLastMessageCount] = useState(0);
  const [isProcessingInterview, setIsProcessingInterview] = useState(false);

  useDebugMode();

  // Find the latest agent (AI) message (not from local user)
  const latestAgentMessage = React.useMemo(
    () => [...messages].reverse().find((msg) => !msg.from?.isLocal),
    [messages],
  );
  // Find the latest user message (answer)
  const latestUserMessage = React.useMemo(
    () => [...messages].reverse().find((msg) => msg.from?.isLocal),
    [messages],
  );

  // Detect when new conversation exchange begins
  useEffect(() => {
    if (messages.length > lastMessageCount) {
      const newMessage = messages[messages.length - 1];

      // If this is a new AI message (after user has spoken), clear previous chat
      if (!newMessage.from?.isLocal && latestUserMessage) {
        setShouldClearChat(true);
        setIsTyping(false);
        setTypingText("");
        setCurrentMessage(null);
      }

      setLastMessageCount(messages.length);
    }
  }, [messages, lastMessageCount, latestUserMessage]);

  // Typing effect for new messages
  useEffect(() => {
    const newMessage = latestAgentMessage || latestUserMessage;

    if (newMessage && newMessage.id !== currentMessage?.id) {
      setIsTyping(true);
      setTypingText("");
      setCurrentMessage(newMessage);

      // Clear screen and start typing
      setTimeout(() => {
        let index = 0;
        const text = newMessage.message;

        const typeInterval = setInterval(() => {
          if (index < text.length) {
            setTypingText(text.substring(0, index + 1));
            index++;
          } else {
            clearInterval(typeInterval);
            setIsTyping(false);
            setShouldClearChat(false); // Reset clear flag after typing is done
          }
        }, typingSpeed);
      }, 500); // Small delay before starting to type
    }
  }, [latestAgentMessage, latestUserMessage, currentMessage, typingSpeed]);

  // Placeholder: send Q&A pair to backend
  async function saveQuestionAnswerPair(question: string, answer: string) {
    // Optionally, get session_id from context or props if available
    const session_id = undefined; // TODO: set if you have a session/interview id
    try {
      await fetch("/api/v1/qa/score", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ question, answer, session_id }),
      });
    } catch (e) {
      console.error("Failed to save Q&A:", e);
    }
  }

  async function handleSendMessage(message: string) {
    await send(message);
    // Save Q&A pair if both question and answer exist
    if (latestAgentMessage && message) {
      await saveQuestionAnswerPair(latestAgentMessage.message, message);
    }
  }

  // Handler for End Call button
  async function handleEndCall() {
    console.log(
      "🔄 End Call button clicked - starting navigation to result page",
    );

    onEndCallStarted?.();

    // Force disconnect face detection immediately
    if (faceDetectionRef.current) {
      console.log("🛑 Force disconnecting face detection");
      faceDetectionRef.current.forceDisconnect();
    }
    setFaceDetectionActive(false);

    // Immediately set hasNavigated to prevent automatic navigation
    setHasNavigated(true);
    setIsProcessingInterview(true);

    // Process interview data FIRST, then navigate
    try {
      console.log("📊 Processing interview data...");
      const sessionId = await processInterviewData();
      console.log("✅ Interview data processed successfully");
      console.log("🚀 Navigating to /result page with sessionId:", sessionId);

      // Navigate with sessionId if available
      if (sessionId) {
        handleRouterPush(`/result?sessionId=${sessionId}`);
      } else {
        handleRouterPush("/result");
      }
    } catch (error) {
      console.error("❌ Error processing interview:", error);
      // Navigate anyway even if processing fails
      handleRouterPush("/result");
    } finally {
      setIsProcessingInterview(false);
    }
  }

  useEffect(() => {
    if (sessionStarted) {
      const timeout = setTimeout(() => {
        if (!isAgentAvailable(agentState)) {
          const reason =
            agentState === "connecting"
              ? "Agent did not join the room. "
              : "Agent connected but did not complete initializing. ";

          toastAlert({
            title: "Session ended",
            description: reason,
          });
          safeDisconnect(room, "session-view-timeout").catch(console.error);
        }
      }, 10_000);

      return () => clearTimeout(timeout);
    }
  }, [agentState, sessionStarted, room]);

  // Detect end of interview (AI says 'have a great day' or 'thank') ONLY if it's the last message and user has answered
  useEffect(() => {
    // Skip if user has already navigated (e.g., by clicking End Call)
    if (hasNavigated) {
      console.log(
        "🚫 Skipping automatic navigation - user has already navigated",
      );
      return;
    }

    // Find the index of the latest agent message
    const lastAgentIdx = messages
      .map((msg) => !msg.from?.isLocal)
      .lastIndexOf(true);
    // Find the index of the latest user message
    const lastUserIdx = messages
      .map((msg) => msg.from?.isLocal)
      .lastIndexOf(true);
    // Normalize message for robust matching
    const normalizedMsg =
      latestAgentMessage?.message
        ?.toLowerCase()
        .replace(/[^a-z0-9 ]/gi, "")
        .trim() || "";
    const endRegex = /(have a great day|thank)/i;
    // Only navigate if:
    // - The latest agent message contains 'have a great day' or 'thank' (robust)
    // - It is the last message in the list
    // - The user has answered the last question (user message comes after or at the same index as agent)
    // - User hasn't manually clicked End Call
    if (
      latestAgentMessage &&
      endRegex.test(normalizedMsg) &&
      messages[messages.length - 1]?.id === latestAgentMessage.id &&
      lastUserIdx >= lastAgentIdx &&
      !hasNavigated
    ) {
      console.log(
        "🤖 AI detected end of interview - starting automatic navigation",
      );

      // Force disconnect face detection immediately
      if (faceDetectionRef.current) {
        console.log("🛑 Force disconnecting face detection");
        faceDetectionRef.current.forceDisconnect();
      }
      setFaceDetectionActive(false);

      setHasNavigated(true);
      setIsProcessingInterview(true);

      // Process and send interview data to backend
      processInterviewData()
        .then((sessionId) => {
          console.log("🚀 Auto-navigating to /result page with sessionId:", sessionId);

          // Navigate with sessionId if available
          if (sessionId) {
            handleRouterPush(`/result?sessionId=${sessionId}`);
          } else {
            handleRouterPush("/result");
          }
        })
        .catch((error) => {
          console.error("❌ Error processing interview:", error);
          handleRouterPush("/result");
        })
        .finally(() => {
          setIsProcessingInterview(false);
        });
    }
  }, [messages, latestAgentMessage, hasNavigated, router]);

  // Function to process and send interview data
  async function processInterviewData(): Promise<string | null> {
    try {
      // Extract questions and answers from conversation
      const questions: string[] = [];
      const answers: string[] = [];
      const conversation = messages.map((msg) => ({
        role: msg.from?.isLocal ? "user" : "assistant",
        content: msg.message,
        timestamp: new Date().toISOString(),
      }));

      console.log("🔍 Processing conversation messages:", messages.length);
      console.log(
        "📝 All messages:",
        messages.map((msg) => ({
          from: msg.from?.isLocal ? "user" : "assistant",
          message: msg.message.substring(0, 100) + "...",
        })),
      );

      // Extract Q&A pairs from messages - improved logic
      const questionAnswerPairs: { question: string; answer: string }[] = [];
      
      // Build a cleaner conversation flow
      const conversationFlow: Array<{ role: string; content: string; index: number }> = [];
      messages.forEach((msg, idx) => {
        conversationFlow.push({
          role: msg.from?.isLocal ? "user" : "assistant",
          content: msg.message.trim(),
          index: idx
        });
      });

      console.log("📋 Full conversation flow:", conversationFlow.map(m => ({
        role: m.role,
        content: m.content.substring(0, 100) + (m.content.length > 100 ? "..." : "")
      })));

      // Improved question detection - look for assistant messages that are questions
      let i = 0;
      while (i < conversationFlow.length && questionAnswerPairs.length < 5) {
        const msg = conversationFlow[i];
        
        if (msg.role === "assistant" && msg.content.length > 10) {
          const messageContent = msg.content.toLowerCase();
          
          // Better question detection - check for question words or question marks
          const hasQuestionMark = msg.content.includes("?");
          const hasQuestionWords = 
            messageContent.includes("what") ||
            messageContent.includes("how") ||
            messageContent.includes("why") ||
            messageContent.includes("when") ||
            messageContent.includes("where") ||
            messageContent.includes("who") ||
            messageContent.includes("can you") ||
            messageContent.includes("tell me") ||
            messageContent.includes("explain") ||
            messageContent.includes("describe");
          
          // Skip obvious non-questions
          const isSimpleGreeting = 
            (messageContent.includes("hello") || 
             messageContent.includes("hi") || 
             messageContent.includes("welcome")) &&
            !hasQuestionMark && 
            !hasQuestionWords &&
            msg.content.length < 50;
          
          const isSimpleClosing = 
            (messageContent.includes("thank you so much") ||
             messageContent.includes("have a great day") ||
             messageContent.includes("we'll be in touch") ||
             messageContent.includes("goodbye")) &&
            !hasQuestionMark;
          
          const isSimpleAcknowledgment = 
            (messageContent.includes("great") ||
             messageContent.includes("excellent") ||
             messageContent.includes("good") ||
             messageContent.includes("thanks")) &&
            !hasQuestionMark &&
            !hasQuestionWords &&
            msg.content.length < 100;

          // If it's a question (has question mark OR question words) and not a simple greeting/closing
          if ((hasQuestionMark || hasQuestionWords) && !isSimpleGreeting && !isSimpleClosing && !isSimpleAcknowledgment) {
            // Clean the question - remove transition phrases and extract only the actual question
            let question = msg.content;
            
            // Remove common transition phrases that come before questions
            const transitionPhrases = [
              /^that'?s?\s+(absolutely\s+)?fine,?\s*no\s+problem\s+(at\s+all)?[.!]?\s*/i,
              /^that'?s?\s+okay,?\s*no\s+worries?[.!]?\s*/i,
              /^great!?\s*/i,
              /^alright,?\s*/i,
              /^perfect[.!]?\s*/i,
              /^thanks?\s+(for\s+that)?[.!]?\s*/i,
              /^okay,?\s*/i,
              /^sure,?\s*no\s+problem[.!]?\s*/i,
              /^let'?s?\s+move\s+on\s+(to\s+the\s+next\s+question)?[.!]?\s*/i,
              /^moving\s+(forward|on)[,.]?\s*/i,
              /^here'?s?\s+(another\s+one\s+for\s+you|the\s+next\s+question)[.!]?\s*/i,
              /^now,?\s*/i,
              /^so,?\s*/i,
              /^well,?\s*/i,
              /^i\s+see[.!]?\s*/i,
              /^got\s+it[.!]?\s*/i,
              /^makes\s+sense[.!]?\s*/i,
              /^interesting[.!]?\s*/i,
              /^good\s+point[.!]?\s*/i,
              /^that'?s?\s+great[.!]?\s*/i,
              /^i\s+see\s+what\s+you\s+mean[.!]?\s*/i,
              /^okay,?\s+that\s+makes\s+sense[.!]?\s*/i,
              /^interesting\s+approach[.!]?\s*/i,
            ];
            
            // Remove transition phrases
            for (const pattern of transitionPhrases) {
              question = question.replace(pattern, '');
            }
            
            // If question starts with "can you tell me" or similar, keep it but clean up
            // Remove redundant phrases like "let me ask you about" or "I'd like to know"
            question = question.replace(/^(let\s+me\s+ask\s+you\s+about|i'?d?\s+like\s+to\s+know|can\s+you\s+tell\s+me)\s*/i, '');
            
            // Clean up multiple spaces and trim
            question = question.replace(/\s+/g, ' ').trim();
            
            // If question is empty after cleaning, use original
            if (!question || question.length < 10) {
              question = msg.content;
            }
            
            console.log(`🎯 Found question ${questionAnswerPairs.length + 1}:`, question);
            
            // Look for the next user message as the answer
            let foundAnswer = false;
            let answer = "";
            
            // Search forward for user response
            for (let j = i + 1; j < conversationFlow.length; j++) {
              const nextMsg = conversationFlow[j];
              
              // If we hit another assistant question, stop searching
              if (nextMsg.role === "assistant" && 
                  (nextMsg.content.includes("?") || 
                   nextMsg.content.toLowerCase().includes("what") ||
                   nextMsg.content.toLowerCase().includes("how") ||
                   nextMsg.content.toLowerCase().includes("can you"))) {
                break;
              }
              
              // Found user answer
              if (nextMsg.role === "user" && nextMsg.content.trim().length > 0) {
                answer = nextMsg.content.trim();
                foundAnswer = true;
                console.log(`💬 Found answer for question ${questionAnswerPairs.length + 1}:`, answer);
                break;
              }
            }
            
            // Add the Q&A pair
            questionAnswerPairs.push({
              question: question,
              answer: foundAnswer ? answer : "No answer provided"
            });
            
            // Skip to after the answer (or after this question if no answer)
            if (foundAnswer) {
              // Find the index of the answer message and skip past it
              for (let k = i + 1; k < conversationFlow.length; k++) {
                if (conversationFlow[k].role === "user" && conversationFlow[k].content.trim() === answer) {
                  i = k + 1;
                  break;
                }
              }
            } else {
              i++;
            }
          } else {
            i++;
          }
        } else {
          i++;
        }
      }
      
      console.log(`✅ Extracted ${questionAnswerPairs.length} Q&A pairs:`, questionAnswerPairs);

      // Extract questions and answers from pairs
      const extractedQuestions = questionAnswerPairs.map(
        (pair) => pair.question,
      );
      const extractedAnswers = questionAnswerPairs.map((pair) => pair.answer);

      // Update the original arrays
      questions.length = 0;
      answers.length = 0;
      questions.push(...extractedQuestions);
      answers.push(...extractedAnswers);

      console.log(
        `📝 Final extraction: ${questions.length} questions and ${answers.length} answers`,
      );
      console.log("📋 Questions:", questions);
      console.log("💬 Answers:", answers);
      
      // Log each pair for debugging
      questionAnswerPairs.forEach((pair, idx) => {
        console.log(`Pair ${idx + 1}:`);
        console.log(`  Q: ${pair.question.substring(0, 100)}${pair.question.length > 100 ? "..." : ""}`);
        console.log(`  A: ${pair.answer.substring(0, 100)}${pair.answer.length > 100 ? "..." : ""}`);
      });

      // Generate session ID
      const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

      // Send to backend for evaluation
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002/api/v1"}/interview/evaluate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            session_id: sessionId,
            conversation: conversation,
            questions: questions,
            answers: answers,
          }),
        },
      );

      if (response.ok) {
        const result = await response.json();

        // Enhance result with face and voice analysis data
        const enhancedResult = {
          ...result,
          face_analysis: faceAnalysisData,
          voice_analysis: {
            speaking: true, // Assume speaking during interview
            confidence: 0.7, // Default confidence
            nervousness: 0.3, // Default nervousness
            speech_patterns: ["Interview speech detected"],
          },
        };

        // Store the enhanced result in localStorage with a consistent key
        const storageKey = `interview_result_${sessionId}`;
        localStorage.setItem(storageKey, JSON.stringify(enhancedResult));

        // Also store the latest session ID for easier retrieval
        localStorage.setItem("latest_interview_session", sessionId);

        // For backward compatibility, also save with the old key
        localStorage.setItem("interviewResult", JSON.stringify(enhancedResult));

        console.log(
          "✅ Interview evaluation completed with enhanced analysis:",
          enhancedResult,
        );

        // Return the session ID for navigation
        return sessionId;
      } else {
        console.error("❌ Failed to evaluate interview:", response.statusText);
        const errorText = await response.text();
        console.error("Error details:", errorText);
        return null;
      }
    } catch (error) {
      console.error("❌ Error processing interview data:", error);
      return null;
    }
  }

  return (
    <main
      ref={ref}
      inert={disabled}
      className="min-h-screen bg-background flex flex-col items-center justify-center"
    >
      {/* Camera Preview - Top Right Corner */}
      {cameraTrack && (
        <div className="fixed top-4 right-4 z-40">
          <div className="w-48 h-36 rounded-lg overflow-hidden shadow-lg border-2 border-gray-200">
            <VideoTile trackRef={cameraTrack} className="w-full h-full" />
          </div>
        </div>
      )}

      {/* Centered Chat Messages */}
      <div className="flex-1 flex items-center justify-center px-4 py-8 w-full max-w-4xl">
        <ChatMessageView className={cn("w-full mx-auto")}>
          <div className="space-y-4 flex flex-col items-center">
            {/* Welcome message when session starts */}
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="text-center w-full max-w-2xl"
              >
                <div className="bg-gray-100 rounded-[20px] p-6 text-gray-900 border border-gray-200">
                  <h3 className="text-xl font-semibold mb-2">
                    Interview Session Started
                  </h3>
                  <p className="text-lg">
                    The AI interviewer will begin shortly. Please wait for the
                    first question.
                  </p>
                  <p className="text-md text-blue-600 mt-2 font-medium">
                    Say "hello" to start the interview
                  </p>
                </div>
              </motion.div>
            )}

            <AnimatePresence>
              {/* Show normal chat when not typing and not clearing */}
              {messages.length > 0 && !isTyping && !shouldClearChat && (
                <div className="w-full max-w-2xl flex flex-col items-center space-y-4">
                  {/* Show AI message second (below) */}
                  {latestAgentMessage && (
                    <motion.div
                      key={`ai-${latestAgentMessage.id}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3, ease: "easeOut" }}
                      className="w-full flex justify-start"
                    >
                      <ChatEntry
                        entry={latestAgentMessage}
                        hideName={false}
                        hideTimestamp={false}
                      />
                    </motion.div>
                  )}
                </div>
              )}

              {/* Typing effect display - shows when new message is being typed */}
              {isTyping && currentMessage && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="w-full max-w-2xl flex flex-col items-center space-y-4"
                >
                  <div
                    className={cn(
                      "w-full flex",
                      currentMessage.from?.isLocal
                        ? "justify-end"
                        : "justify-start",
                    )}
                  >
                    <div
                      className={cn(
                        "w-full max-w-4/5 rounded-[20px] p-3 text-base leading-relaxed shadow-sm min-h-[50px] flex items-center",
                        currentMessage.from?.isLocal
                          ? "bg-blue-100 text-blue-900 border border-blue-200 ml-auto"
                          : "bg-gray-100 text-gray-900 border border-gray-200 mr-auto",
                      )}
                    >
                      <span className="w-full">
                        {typingText}
                        <span className="animate-pulse">|</span>
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Show blank screen when clearing chat */}
              {shouldClearChat && !isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="w-full max-w-2xl flex flex-col items-center"
                >
                  <div className="w-full bg-gray-100 rounded-[20px] p-4 text-gray-900 border border-gray-200 text-center">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                      <span className="text-base font-medium">
                        Preparing next question...
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </ChatMessageView>
      </div>

      {/* Processing Overlay */}
      {isProcessingInterview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold mb-2">Processing Interview</h3>
            <p className="text-muted-foreground">Analyzing your responses...</p>
          </div>
        </div>
      )}

      {/* Face Detection Toggle - Fixed at top right */}
      <div className="fixed top-4 right-4 z-50">
        <FaceDetectionToggle
          isActive={faceDetectionActive}
          onToggle={() => setFaceDetectionActive(!faceDetectionActive)}
          disabled={disabled}
          isCameraRunning={faceDetectionActive}
        />
      </div>

      {/* Face Detection Panel */}
      <FaceDetectionPanel
        ref={faceDetectionRef}
        isActive={faceDetectionActive}
        onToggle={() => setFaceDetectionActive(false)}
        shouldStartCamera={faceDetectionActive}
        onAnalysisDataChange={setFaceAnalysisData}
      />

      {/* Agent Control Bar - Fixed at bottom */}
      <div className="fixed bottom-8 left-1/2 z-50 -translate-x-1/2">
        <AgentControlBar
          capabilities={{
            supportsChatInput: appConfig.supportsChatInput,
            supportsVideoInput: appConfig.supportsVideoInput,
            supportsScreenShare: appConfig.supportsScreenShare,
          }}
          onChatOpenChange={setChatOpen}
          onSendMessage={handleSendMessage}
          onDisconnect={async () => {
            await handleEndCall();
            // Add a small delay to ensure navigation completes before disconnect
            setTimeout(() => {
              safeDisconnect(room, "session-view-control-bar").catch(
                console.error,
              );
            }, 200);
          }}
          onDeviceError={(error) => {
            toastAlert({
              title: "Device Error",
              description: `${error.source}: ${error.error.message}`,
            });
          }}
        />
      </div>
    </main>
  );
};
