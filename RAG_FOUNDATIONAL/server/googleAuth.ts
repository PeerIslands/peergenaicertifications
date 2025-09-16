import "dotenv/config";
import passport from "passport";
import session from "express-session";
import MongoStore from "connect-mongo";
import type { Express, RequestHandler } from "express";
import { Strategy as GoogleStrategy, type Profile, type VerifyCallback } from "passport-google-oauth20";
import { storage } from "./storage";

// Google OAuth 2.0 configuration using passport-google-oauth20

export function getSession() {
  const sessionTtl = 7 * 24 * 60 * 60 * 1000; // 1 week
  const isHttps = (process.env.APP_BASE_URL || "").startsWith("https://");
  const sessionStore = MongoStore.create({
    mongoUrl: process.env.DATABASE_URL!,
    dbName: process.env.MONGODB_DB || "rag_application",
    ttl: Math.floor(sessionTtl / 1000),
    collectionName: "sessions",
    autoRemove: "native",
  });
  return session({
    secret: process.env.SESSION_SECRET!,
    store: sessionStore,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: isHttps,
      sameSite: "lax",
      maxAge: sessionTtl,
    },
  });
}

function updateUserSession(user: any, claims: any, accessToken?: string, refreshToken?: string) {
  user.claims = claims;
  user.access_token = accessToken;
  user.refresh_token = refreshToken;
}

async function upsertUser(
  claims: any,
) {
  await storage.upsertUser({
    id: claims["sub"],
    email: claims["email"],
    firstName: claims["first_name"],
    lastName: claims["last_name"],
    profileImageUrl: claims["profile_image_url"],
  });
}

export async function setupAuth(app: Express) {
  app.set("trust proxy", 1);
  app.use(getSession());
  app.use(passport.initialize());
  app.use(passport.session());

  passport.use(
    new GoogleStrategy(
      {
        clientID: process.env.GOOGLE_CLIENT_ID!,
        clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        callbackURL: `${process.env.APP_BASE_URL}/api/callback`,
      },
      async (accessToken: string, refreshToken: string, profile: Profile, done: VerifyCallback) => {
        try {
          const claims = {
            sub: profile.id,
            email: profile.emails && profile.emails[0] ? profile.emails[0].value : undefined,
            first_name: profile.name?.givenName,
            last_name: profile.name?.familyName,
            profile_image_url: profile.photos && profile.photos[0] ? profile.photos[0].value : undefined,
          };

          const user: any = {};
          updateUserSession(user, claims, accessToken, refreshToken);
          await upsertUser(claims);
          done(null, user);
        } catch (err) {
          done(err as any);
        }
      }
    )
  );

  passport.serializeUser((user: Express.User, cb) => cb(null, user));
  passport.deserializeUser((user: Express.User, cb) => cb(null, user));

  app.get("/api/login", (req, res, next) => {
    passport.authenticate("google", { scope: ["profile", "email"] })(req, res, next);
  });

  app.get(
    "/api/callback",
    passport.authenticate("google", { failureRedirect: "/api/login" }),
    (req, res) => {
      // After successful login, ensure the session is saved before redirecting
      req.session.save(() => {
        res.redirect("/");
      });
    }
  );

  app.get("/api/logout", (req, res) => {
    req.logout(() => {
      const sess = (req as any).session;
      const isHttps = (process.env.APP_BASE_URL || "").startsWith("https://");
      if (sess && typeof sess.destroy === "function") {
        sess.destroy(() => {
          res.clearCookie("connect.sid", {
            httpOnly: true,
            secure: isHttps,
            sameSite: "lax",
            path: "/",
          });
          res.redirect("/");
        });
      } else {
        res.clearCookie("connect.sid", {
          httpOnly: true,
          secure: isHttps,
          sameSite: "lax",
          path: "/",
        });
        res.redirect("/");
      }
    });
  });
}

export const isAuthenticated: RequestHandler = async (req, res, next) => {
  if (!req.isAuthenticated()) {
    return res.status(401).json({ message: "Unauthorized" });
  }
  return next();
};