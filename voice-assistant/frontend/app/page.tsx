"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Target,
  MessageSquare,
  CheckCircle2,
  Zap,
  Users,
  BarChart3,
} from "lucide-react";
import { motion } from "motion/react";
import HomeNav from "@/components/home-nav";
import HomeFooter from "@/components/home-footer";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const trustStrip = [
  "Run 1000+ interviews in parallel",
  "Structured, bias-free evaluation",
  "Instant candidate scoring",
  "No scheduling. No coordination.",
];

const valueCards = [
  {
    icon: MessageSquare,
    title: "AI Interviews That Actually Work",
    description:
      "AI doesn't just ask questions — it adapts, probes deeper, and evaluates candidates in real time.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Target,
    title: "Know Who to Hire — Instantly",
    description:
      "Every candidate comes with a score, strengths, weaknesses, and a clear recommendation.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: Zap,
    title: "Built for Real Hiring Workflows",
    description:
      "Define a role once. AI handles technical + behavioral screening automatically.",
    gradient: "from-orange-500 to-red-500",
  },
  {
    icon: BarChart3,
    title: "Data, Not Gut Feeling",
    description:
      "Make decisions based on structured insights, not inconsistent interviews.",
    gradient: "from-green-500 to-emerald-500",
  },
];

const steps = [
  {
    number: "01",
    title: "Define the Role",
    description:
      "Tell us what you're hiring for. Skills, experience, expectations.",
    icon: Users,
  },
  {
    number: "02",
    title: "AI Runs Interviews",
    description:
      "Candidates complete intelligent, adaptive interviews — anytime.",
    icon: MessageSquare,
  },
  {
    number: "03",
    title: "Get Ranked Candidates",
    description:
      "Scores, summaries, and top candidates — ready for your team to review.",
    icon: BarChart3,
  },
];

const outcomes = [
  "Only top candidates reach your team",
  "Consistent evaluation across all applicants",
  "Faster hiring decisions",
  "Scalable hiring process",
];

const builtFor = [
  "Startups hiring fast without scaling recruiters",
  "HR teams handling high-volume applications",
  "Tech companies running technical + behavioral screens",
];

export default function Page() {
  return (
    <div className="min-h-screen bg-background overflow-hidden">
      <HomeNav />

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-6">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
          <div className="absolute top-40 right-20 w-96 h-96 bg-accent/30 rounded-full blur-3xl" />
          <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-primary/10 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto relative">
          <motion.div
            className="max-w-4xl mx-auto text-center"
            initial="initial"
            animate="animate"
            variants={staggerContainer}
          >
            <motion.div
              variants={fadeInUp}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-semibold mb-8"
            >
              Save time. Save money. Hire smarter.
            </motion.div>

            <motion.h1
              variants={fadeInUp}
              className="text-5xl md:text-6xl lg:text-7xl font-bold text-foreground leading-[1.1] mb-5"
            >
              AI-Powered Screening That Fits Your Time.
            </motion.h1>

            <motion.p
              variants={fadeInUp}
              className="text-xl md:text-2xl text-foreground font-medium max-w-2xl mx-auto mb-4"
            >
              AI helps recruiters conduct, evaluate, and shortlist candidates — in less time.
            </motion.p>

            <motion.p
              variants={fadeInUp}
              className="text-lg text-muted-foreground max-w-xl mx-auto mb-10"
            >
              Spend less time on screening. Save money. Focus on candidates who matter.
            </motion.p>

            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Link href="/signup">
                <Button variant="hero" size="xl" className="min-w-[200px]">
                  Book Demo
                </Button>
              </Link>
              <Button variant="hero-outline" size="xl" className="min-w-[200px]">
                See It in Action
              </Button>
            </motion.div>

            <motion.div
              variants={fadeInUp}
              className="flex flex-wrap items-center justify-center gap-x-8 gap-y-4 mt-12"
            >
              {trustStrip.map((text) => (
                <div
                  key={text}
                  className="flex items-center gap-2 text-sm font-medium text-foreground"
                >
                  <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
                  {text}
                </div>
              ))}
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Value Section — Stop Screening. Start Deciding. */}
      <section className="py-24 px-6">
        <div className="container mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold text-foreground mb-4">
              Less Screening Time. Better Decisions.
            </h2>
            <p className="text-foreground/80 text-lg max-w-2xl mx-auto font-medium">
              Outcome-driven hiring that saves recruiters time and money.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {valueCards.map((card, index) => (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="group relative p-6 rounded-2xl bg-card border border-border hover:border-primary/30 hover:shadow-elevated transition-all duration-500"
              >
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative">
                  <div
                    className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${card.gradient} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
                  >
                    <card.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground mb-3">
                    {card.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {card.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works — From Resume to Shortlist */}
      <section className="py-24 px-6 bg-card border-y border-border">
        <div className="container mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold text-foreground mb-4">
              From Resume to Shortlist — in Minutes
            </h2>
            <p className="text-foreground/80 text-lg max-w-xl mx-auto font-medium">
              Three steps. No scheduling. No chaos.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto relative">
            <div className="hidden md:block absolute top-24 left-[20%] right-[20%] h-0.5 bg-gradient-to-r from-primary/20 via-primary to-primary/20" />

            {steps.map((step, index) => (
              <motion.div
                key={step.number}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15 }}
                className="relative text-center"
              >
                <div className="relative inline-flex items-center justify-center w-20 h-20 rounded-full bg-background border-4 border-primary mb-6">
                  <step.icon className="w-8 h-8 text-primary" />
                  <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-bold flex items-center justify-center">
                    {step.number.replace("0", "")}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  {step.title}
                </h3>
                <p className="text-muted-foreground">{step.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* What You Get Instead */}
      <section className="py-20 px-6 bg-muted/20 border-y border-border">
        <div className="container mx-auto max-w-4xl">
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-4xl font-bold text-foreground text-center mb-12"
          >
            What You Get
          </motion.h2>
          <ul className="grid sm:grid-cols-2 gap-4">
            {outcomes.map((point, i) => (
              <motion.li
                key={point}
                initial={{ opacity: 0, x: 12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06 }}
                className="flex items-center gap-3 p-4 rounded-xl bg-card border border-border"
              >
                <CheckCircle2 className="w-5 h-5 text-primary shrink-0" />
                <span className="text-foreground font-semibold">{point}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      </section>

      {/* Who This Is For (Built For) */}
      <section className="py-24 px-6">
        <div className="container mx-auto max-w-4xl">
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-4xl font-bold text-foreground text-center mb-12"
          >
            Who This Is For
          </motion.h2>
          <div className="space-y-4">
            {builtFor.map((item, i) => (
              <motion.div
                key={item}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="p-5 rounded-2xl bg-card border border-border text-center md:text-left"
              >
                <span className="text-foreground font-semibold">{item}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-16 lg:py-20 px-6 bg-muted/40 border-y border-border">
        <div className="container mx-auto max-w-2xl text-center">
          <motion.h2
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-3xl md:text-5xl font-bold text-foreground mb-4"
          >
            Start Hiring Smarter Today
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-lg text-foreground/80 font-medium mb-10 max-w-xl mx-auto"
          >
            Let AI support your screening — so your team saves time and focuses on the right candidates.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <Link href="/signup">
              <Button size="lg" className="min-w-[180px]">
                Book Demo
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      <HomeFooter />
    </div>
  );
}
