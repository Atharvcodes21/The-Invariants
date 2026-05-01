// Firebase client configuration
import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey:            process.env.NEXT_PUBLIC_FIREBASE_API_KEY            || "AIzaSyBZpNUcc4q66rIl6_1-_vIIK1Om3XEsWYw",
  authDomain:        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN        || "voicerx-62c31.firebaseapp.com",
  projectId:         process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID         || "voicerx-62c31",
  storageBucket:     process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET     || "voicerx-62c31.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "218772486202",
  appId:             process.env.NEXT_PUBLIC_FIREBASE_APP_ID             || "1:218772486202:web:dac1194309069f50c81d03",
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
export const auth     = getAuth(app);
export const provider = new GoogleAuthProvider();
