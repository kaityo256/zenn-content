# frozen_string_literal: true

require "json"

def load_zenn_json(path, articles)
  unless File.file?(path)
    raise ArgumentError, "File not found: #{path}"
  end

  raw = File.read(path, encoding: "UTF-8")
  data = JSON.parse(raw) # => Hash or Array

  unless data.is_a?(Hash)
    raise TypeError, "Expected top-level JSON object (Hash), got: #{data.class}"
  end

  data['articles'].each do |a|
    articles.append a
  end
rescue JSON::ParserError => e
  raise JSON::ParserError, "Invalid JSON in #{path}: #{e.message}"
end

def strip_front_matter(content)
  if content =~ /\A---\s*\n/
    content.sub(/\A---\s*\n.*?\n---\s*\n/m, '')
  else
    content
  end
end

def rewrite_image_paths(content)
  content = content.gsub("](/images/", "](/assets/images/")
  content
end

def export_article(article)
  slug = article['slug']
  filename = '../articles/'+slug+'.md'
  content = File.read(filename)
  content = strip_front_matter(content)
  content = rewrite_image_paths(content)
  fmatter = front_matter(article)
  content = fmatter + content
  export_file = 'mysite/_posts/' + slug + '.md'
  puts export_file
  File.write(export_file, content)
end

def front_matter(article)
  fmatter = <<-"EOS"
---
layout: post
title: #{article['title']}
tags: [zenn]
permalink: #{article['slug']}
---

# #{article['title']}

  EOS
  fmatter
end

articles = []

load_zenn_json("zenn1.json", articles)
load_zenn_json("zenn2.json", articles)

articles.each do |article|
  export_article(article)
end