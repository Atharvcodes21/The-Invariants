// Firebase client configuration
import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey:            "AIzaSyBZpNUcc4q66rIl6_1-_vIIK1Om3XEsWYw",
  authDomain:        "voicerx-62c31.firebaseapp.com",
  projectId:         "voicerx-62c31",
  storageBucket:     "voicerx-62c31.firebasestorage.app",
  messagingSenderId: "218772486202",
  appId:             "1:218772486202:web:dac1194309069f50c81d03",
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
export const auth     = getAuth(app);
export const provider = new GoogleAuthProvider();
